use crate::config::AppConfig;
use crate::packet::{HttpPacket, PacketCapture};
use anyhow::Result;
use reqwest::Client;
use serde_json::Value;
use std::collections::HashMap;
use tracing::{info, warn, error};

pub struct MenuScraper {
    client: Client,
    config: AppConfig,
    capture: PacketCapture,
}

impl MenuScraper {
    pub fn new(config: AppConfig) -> Result<Self> {
        let client = Client::builder()
            .timeout(std::time::Duration::from_secs(30))
            .build()?;
        
        Ok(Self {
            client,
            config,
            capture: PacketCapture::new(),
        })
    }
    
    pub async fn load_captured_packets(&mut self, path: &str) -> Result<()> {
        let content = std::fs::read_to_string(path)?;
        let packets: Vec<Value> = serde_json::from_str(&content)?;
        
        for packet_json in packets {
            if let Ok(packet) = HttpPacket::from_mitmproxy_json(&packet_json.to_string()) {
                self.capture.add_packet(packet);
            }
        }
        
        info!("加载了 {} 个抓包数据", self.capture.packets.len());
        Ok(())
    }
    
    pub async fn scrape_menu(&self, restaurant_id: &str) -> Result<Vec<FoodItem>> {
        let endpoint = self.config.endpoints.get("menu")
            .ok_or_else(|| anyhow::anyhow!("未找到菜单API端点"))?;
        
        let url = format!("{}{}", 
            self.config.base_url,
            endpoint.url.replace("{restaurant_id}", restaurant_id)
        );
        
        let mut request = match endpoint.method.as_str() {
            "GET" => self.client.get(&url),
            "POST" => self.client.post(&url),
            _ => anyhow::bail!("不支持的HTTP方法"),
        };
        
        // 添加认证头
        if let Some(token) = &self.config.auth_token {
            request = request.header("Authorization", format!("Bearer {}", token));
        }
        
        // 添加自定义头
        for (key, value) in &endpoint.headers {
            request = request.header(key, value);
        }
        
        let response = request.send().await?;
        
        if response.status().is_success() {
            let data: Value = response.json().await?;
            let items = self.parse_menu_response(&data)?;
            Ok(items)
        } else {
            error!("获取菜单失败: {}", response.status());
            anyhow::bail!("请求失败: {}", response.status())
        }
    }
    
    fn parse_menu_response(&self, data: &Value) -> Result<Vec<FoodItem>> {
        let mut items = Vec::new();
        
        // 根据实际API响应结构调整
        if let Some(menu_array) = data["menu"].as_array() {
            for item_json in menu_array {
                let item = FoodItem {
                    id: item_json["id"].as_str().unwrap_or_default().to_string(),
                    name: item_json["name"].as_str().unwrap_or_default().to_string(),
                    price: item_json["price"].as_f64().unwrap_or(0.0),
                    description: item_json["description"].as_str().map(|s| s.to_string()),
                    category: item_json["category"].as_str().map(|s| s.to_string()),
                    image_url: item_json["image_url"].as_str().map(|s| s.to_string()),
                };
                items.push(item);
            }
        }
        
        Ok(items)
    }
    
    pub fn analyze_captured_data(&self) -> Result<AnalysisResult> {
        let domains = self.capture.get_unique_domains();
        let api_patterns = self.capture.analyze_api_patterns();
        
        let mut auth_packets = Vec::new();
        let mut menu_packets = Vec::new();
        let mut order_packets = Vec::new();
        
        for packet in &self.capture.packets {
            if packet.url.contains("auth") || packet.url.contains("login") {
                auth_packets.push(packet);
            } else if packet.url.contains("menu") || packet.url.contains("food") {
                menu_packets.push(packet);
            } else if packet.url.contains("order") {
                order_packets.push(packet);
            }
        }
        
        Ok(AnalysisResult {
            total_packets: self.capture.packets.len(),
            domains,
            api_patterns,
            auth_endpoints: auth_packets.len(),
            menu_endpoints: menu_packets.len(),
            order_endpoints: order_packets.len(),
        })
    }
    
    pub fn extract_api_endpoints(&self) -> Result<HashMap<String, Vec<String>>> {
        let mut endpoints = HashMap::new();
        
        for packet in &self.capture.packets {
            let path = packet.url.split('?').next().unwrap_or(&packet.url);
            endpoints.entry(path.to_string())
                .or_insert_with(Vec::new)
                .push(packet.method.clone());
        }
        
        Ok(endpoints)
    }
}

#[derive(Debug)]
pub struct FoodItem {
    pub id: String,
    pub name: String,
    pub price: f64,
    pub description: Option<String>,
    pub category: Option<String>,
    pub image_url: Option<String>,
}

#[derive(Debug)]
pub struct AnalysisResult {
    pub total_packets: usize,
    pub domains: Vec<String>,
    pub api_patterns: HashMap<String, Vec<String>>,
    pub auth_endpoints: usize,
    pub menu_endpoints: usize,
    pub order_endpoints: usize,
}