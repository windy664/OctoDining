use serde::{Deserialize, Serialize};
use std::collections::HashMap;

#[derive(Debug, Serialize, Deserialize)]
pub struct ApiEndpoint {
    pub name: String,
    pub url: String,
    pub method: String,
    pub headers: HashMap<String, String>,
    pub body_template: Option<String>,
}

#[derive(Debug, Serialize, Deserialize)]
pub struct AppConfig {
    pub base_url: String,
    pub endpoints: HashMap<String, ApiEndpoint>,
    pub auth_token: Option<String>,
    pub restaurant_id: Option<String>,
}

impl AppConfig {
    pub fn load_from_file(path: &str) -> anyhow::Result<Self> {
        let content = std::fs::read_to_string(path)?;
        let config: AppConfig = serde_json::from_str(&content)?;
        Ok(config)
    }
    
    pub fn save_to_file(&self, path: &str) -> anyhow::Result<()> {
        let content = serde_json::to_string_pretty(self)?;
        std::fs::write(path, content)?;
        Ok(())
    }
    
    pub fn create_sample_config() -> Self {
        let mut endpoints = HashMap::new();
        
        endpoints.insert("login".to_string(), ApiEndpoint {
            name: "登录".to_string(),
            url: "/api/auth/login".to_string(),
            method: "POST".to_string(),
            headers: HashMap::new(),
            body_template: Some(r#"{"code": "{code}"}"#.to_string()),
        });
        
        endpoints.insert("menu".to_string(), ApiEndpoint {
            name: "获取菜单".to_string(),
            url: "/api/menu/{restaurant_id}".to_string(),
            method: "GET".to_string(),
            headers: HashMap::new(),
            body_template: None,
        });
        
        endpoints.insert("order".to_string(), ApiEndpoint {
            name: "下单".to_string(),
            url: "/api/order".to_string(),
            method: "POST".to_string(),
            headers: HashMap::new(),
            body_template: Some(r#"{"restaurant_id": "{restaurant_id}", "items": "{items}"}"#.to_string()),
        });
        
        AppConfig {
            base_url: "https://api.example.com".to_string(),
            endpoints,
            auth_token: None,
            restaurant_id: None,
        }
    }
}