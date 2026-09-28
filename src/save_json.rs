use serde_json::Value;
use std::collections::HashMap;

#[tokio::main]
async fn main() -> anyhow::Result<()> {
    let token_content = std::fs::read_to_string("token.json")?;
    let token_data: Value = serde_json::from_str(&token_content)?;
    let token = token_data["token"].as_str().unwrap();
    let store_id = token_data["store_id"].as_str().unwrap();
    
    let client = reqwest::Client::new();
    let url = "https://wxservice-stg69.pospal.cn/wxapi/product/categories";
    
    let mut data = HashMap::new();
    data.insert("storeId", store_id);
    data.insert("includeAllProducts", "true");
    
    let response = client.post(url)
        .header("PSPLVISITORID", token)
        .header("STOREID", store_id)
        .form(&data)
        .send()
        .await?;
    
    let result: Value = response.json().await?;
    std::fs::write("menu.json", serde_json::to_string_pretty(&result)?)?;
    println!("菜单已保存到 menu.json");
    Ok(())
}
