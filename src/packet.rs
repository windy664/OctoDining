use serde::{Deserialize, Serialize};
use std::collections::HashMap;

#[derive(Debug, Serialize, Deserialize)]
pub struct HttpPacket {
    pub id: String,
    pub timestamp: chrono::DateTime<chrono::Utc>,
    pub method: String,
    pub url: String,
    pub headers: HashMap<String, String>,
    pub body: Option<String>,
    pub response_status: Option<u16>,
    pub response_body: Option<String>,
}

#[derive(Debug, Serialize, Deserialize)]
pub struct PacketCapture {
    pub packets: Vec<HttpPacket>,
}

impl PacketCapture {
    pub fn new() -> Self {
        Self {
            packets: Vec::new(),
        }
    }
    
    pub fn add_packet(&mut self, packet: HttpPacket) {
        self.packets.push(packet);
    }
    
    pub fn filter_by_domain(&self, domain: &str) -> Vec<&HttpPacket> {
        self.packets.iter()
            .filter(|p| p.url.contains(domain))
            .collect()
    }
    
    pub fn filter_by_path(&self, path: &str) -> Vec<&HttpPacket> {
        self.packets.iter()
            .filter(|p| p.url.contains(path))
            .collect()
    }
    
    pub fn get_unique_domains(&self) -> Vec<String> {
        let mut domains: Vec<String> = self.packets.iter()
            .filter_map(|p| {
                if let Some(host) = p.headers.get("Host") {
                    Some(host.clone())
                } else {
                    // 尝试从URL提取域名
                    if let Some(domain) = p.url.split("://").nth(1) {
                        if let Some(domain) = domain.split('/').next() {
                            Some(domain.to_string())
                        } else {
                            None
                        }
                    } else {
                        None
                    }
                }
            })
            .collect();
        domains.sort();
        domains.dedup();
        domains
    }
    
    pub fn analyze_api_patterns(&self) -> HashMap<String, Vec<String>> {
        let mut patterns: HashMap<String, Vec<String>> = HashMap::new();
        
        for packet in &self.packets {
            let path = if let Some(path) = packet.url.split('?').next() {
                path.to_string()
            } else {
                packet.url.clone()
            };
            
            patterns.entry(path)
                .or_insert_with(Vec::new)
                .push(packet.method.clone());
        }
        
        patterns
    }
}

impl HttpPacket {
    pub fn from_mitmproxy_json(json_str: &str) -> anyhow::Result<Self> {
        // 解析mitmproxy导出的JSON格式
        let value: serde_json::Value = serde_json::from_str(json_str)?;
        
        let id = value["id"].as_str().unwrap_or_default().to_string();
        let timestamp = chrono::Utc::now(); // 简化处理
        let method = value["request"]["method"].as_str().unwrap_or("GET").to_string();
        let url = value["request"]["url"].as_str().unwrap_or_default().to_string();
        
        let mut headers = HashMap::new();
        if let Some(headers_obj) = value["request"]["headers"].as_object() {
            for (key, val) in headers_obj {
                if let Some(val_str) = val.as_str() {
                    headers.insert(key.clone(), val_str.to_string());
                }
            }
        }
        
        let body = value["request"]["content"].as_str().map(|s| s.to_string());
        let response_status = value["response"]["status_code"].as_u64().map(|s| s as u16);
        let response_body = value["response"]["content"].as_str().map(|s| s.to_string());
        
        Ok(Self {
            id,
            timestamp,
            method,
            url,
            headers,
            body,
            response_status,
            response_body,
        })
    }
}