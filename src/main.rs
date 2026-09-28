mod data;
mod algorithm;
mod html;

use std::fs;
use serde_json;

fn main() -> anyhow::Result<()> {
    println!("🍜 广软智能餐表生成器 (Rust版)");
    println!("================================");
    
    // 加载和清洗数据
    println!("正在加载数据...");
    let products = data::load_and_clean_csv("menu.csv")?;
    println!("清洗后商品数: {}", products.len());
    
    // 保存清洗后的数据为JSON
    let products_json = serde_json::to_string(&products)?;
    fs::write("products_clean.json", &products_json)?;
    println!("已保存清洗后数据到 products_clean.json");
    
    // 获取档次配置
    let tiers = data::get_tiers();
    
    // 为每个档次生成餐表
    for (label, tier) in &tiers {
        println!("\n正在生成 {} 的餐表...", tier.name);
        
        let plan = algorithm::generate_meal_plan(&products, tier);
        
        // 打印餐表
        let weekly_total: f64 = plan.iter().map(|d| d.total).sum();
        let daily_avg = weekly_total / 7.0;
        let monthly_avg = daily_avg * 30.0;
        let night_count = plan.iter().filter(|d| d.night_snack.is_some()).count();
        let fruit_count = plan.iter().filter(|d| d.fruit.is_some()).count();
        let coffee_count = plan.iter().filter(|d| d.coffee.is_some()).count();
        
        println!("\n{}", "=".repeat(60));
        println!("  📋 {} - 本周推荐餐表", tier.name);
        println!("  💰 预算: ¥{:.0}/天", tier.daily_budget);
        println!("{}", "=".repeat(60));
        
        for day in &plan {
            println!("\n📅 {} - ¥{:.2}", day.day, day.total);
            if let Some(b) = &day.breakfast {
                println!("  🌅 早餐: {} - ¥{:.2} ({})", b.name, b.price, b.store);
            }
            if let Some(l) = &day.lunch {
                println!("  ☀️ 午餐: {} - ¥{:.2} ({})", l.name, l.price, l.store);
            }
            if let Some(d) = &day.dinner {
                println!("  🌙 晚餐: {} - ¥{:.2} ({})", d.name, d.price, d.store);
            }
            if let Some(c) = &day.coffee {
                println!("  ☕ 下午茶: {} - ¥{:.2} ({})", c.name, c.price, c.store);
            }
            if let Some(n) = &day.night_snack {
                println!("  🌃 夜宵: {} - ¥{:.2} ({})", n.name, n.price, n.store);
            }
            if let Some(f) = &day.fruit {
                println!("  🍎 水果: {} - ¥{:.2} ({})", f.name, f.price, f.store);
            }
        }
        
        println!("\n{}", "-".repeat(60));
        println!("  📊 本周合计: ¥{:.2}", weekly_total);
        println!("  📊 日均花费: ¥{:.2}", daily_avg);
        println!("  📊 月均花费: ¥{:.0}", monthly_avg);
        println!("  ☕ 下午茶: {}次 | 🌃 夜宵: {}次 | 🍎 水果: {}次", coffee_count, night_count, fruit_count);
        println!("{}", "-".repeat(60));
        
        // 生成CSV
        let mut csv = String::from("日期,档次,早餐,早餐价格,午餐,午餐价格,晚餐,晚餐价格,下午茶,下午茶价格,夜宵,夜宵价格,水果,水果价格,当日合计\n");
        for d in &plan {
            csv.push_str(&format!("{},{},{},{},{},{},{},{},{},{},{},{},{},{},{}\n",
                d.day, tier.name,
                d.breakfast.as_ref().map(|b| b.name.as_str()).unwrap_or(""),
                d.breakfast.as_ref().map(|b| b.price).unwrap_or(0.0),
                d.lunch.as_ref().map(|l| l.name.as_str()).unwrap_or(""),
                d.lunch.as_ref().map(|l| l.price).unwrap_or(0.0),
                d.dinner.as_ref().map(|d| d.name.as_str()).unwrap_or(""),
                d.dinner.as_ref().map(|d| d.price).unwrap_or(0.0),
                d.coffee.as_ref().map(|c| c.name.as_str()).unwrap_or(""),
                d.coffee.as_ref().map(|c| c.price).unwrap_or(0.0),
                d.night_snack.as_ref().map(|n| n.name.as_str()).unwrap_or(""),
                d.night_snack.as_ref().map(|n| n.price).unwrap_or(0.0),
                d.fruit.as_ref().map(|f| f.name.as_str()).unwrap_or(""),
                d.fruit.as_ref().map(|f| f.price).unwrap_or(0.0),
                d.total
            ));
        }
        fs::write(format!("meal_plan_{}.csv", label), csv)?;
        println!("已导出 meal_plan_{}.csv", label);
    }
    
    // 生成HTML
    println!("\n正在生成HTML报告...");
    let html_content = html::generate_html(&products_json, &[], "A3 普通级", "A3");
    fs::write("meal_planner.html", html_content)?;
    println!("已生成 meal_planner.html");
    
    println!("\n✅ 完成！");
    
    Ok(())
}