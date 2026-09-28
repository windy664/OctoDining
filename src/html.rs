use crate::data::*;

pub fn generate_html(products_json: &str, plan: &[DayMeal], tier_name: &str, tier_label: &str) -> String {
    let weekly_total: f64 = plan.iter().map(|d| d.total).sum();
    let daily_avg = weekly_total / 7.0;
    let monthly_avg = daily_avg * 30.0;
    let night_count = plan.iter().filter(|d| d.night_snack.is_some()).count();
    let fruit_count = plan.iter().filter(|d| d.fruit.is_some()).count();
    let coffee_count = plan.iter().filter(|d| d.coffee.is_some()).count();
    
    let days_html: String = plan.iter().map(|d| {
        let mut meals_html = String::new();
        
        // 早餐
        if let Some(b) = &d.breakfast {
            meals_html.push_str(&format!(r#"
                <div class="meal-slot">
                    <div class="meal-label">🌅 早餐 (8:00)</div>
                    <div class="meal-name">{}</div>
                    <div class="meal-info">
                        <span class="meal-store">{}</span>
                        <span class="meal-price">¥{:.2}</span>
                    </div>
                </div>"#, b.name, b.store, b.price));
        }
        
        // 午餐
        if let Some(l) = &d.lunch {
            meals_html.push_str(&format!(r#"
                <div class="meal-slot">
                    <div class="meal-label">☀️ 午餐 (12:00)</div>
                    <div class="meal-name">{}</div>
                    <div class="meal-info">
                        <span class="meal-store">{}</span>
                        <span class="meal-price">¥{:.2}</span>
                    </div>
                </div>"#, l.name, l.store, l.price));
        }
        
        // 晚餐
        if let Some(dinner) = &d.dinner {
            meals_html.push_str(&format!(r#"
                <div class="meal-slot">
                    <div class="meal-label">🌙 晚餐 (18:00)</div>
                    <div class="meal-name">{}</div>
                    <div class="meal-info">
                        <span class="meal-store">{}</span>
                        <span class="meal-price">¥{:.2}</span>
                    </div>
                </div>"#, dinner.name, dinner.store, dinner.price));
        }
        
        // 下午茶
        if let Some(c) = &d.coffee {
            meals_html.push_str(&format!(r#"
                <div class="meal-slot">
                    <div class="meal-label">☕ 下午茶 (15:00)</div>
                    <div class="meal-name">{}<span class="tag tag-coffee">下午茶</span></div>
                    <div class="meal-info">
                        <span class="meal-store">{}</span>
                        <span class="meal-price">¥{:.2}</span>
                    </div>
                </div>"#, c.name, c.store, c.price));
        }
        
        // 夜宵
        if let Some(n) = &d.night_snack {
            meals_html.push_str(&format!(r#"
                <div class="meal-slot">
                    <div class="meal-label">🌃 夜宵 (22:00)</div>
                    <div class="meal-name">{}<span class="tag tag-night">夜宵</span></div>
                    <div class="meal-info">
                        <span class="meal-store">{}</span>
                        <span class="meal-price">¥{:.2}</span>
                    </div>
                </div>"#, n.name, n.store, n.price));
        }
        
        // 水果
        if let Some(f) = &d.fruit {
            meals_html.push_str(&format!(r#"
                <div class="meal-slot">
                    <div class="meal-label">🍎 饭后水果</div>
                    <div class="meal-name">{}<span class="tag tag-fruit">水果</span></div>
                    <div class="meal-info">
                        <span class="meal-store">{}</span>
                        <span class="meal-price">¥{:.2}</span>
                    </div>
                </div>"#, f.name, f.store, f.price));
        }
        
        format!(r#"
            <div class="day-card">
                <div class="day-header">
                    <span>📅 {}</span>
                    <span class="day-total">¥{:.2}</span>
                </div>
                {}
            </div>"#, d.day, d.total, meals_html)
    }).collect();
    
    format!(r#"<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>广软智能餐表生成器</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ 
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }}
        .container {{ max-width: 1200px; margin: 0 auto; }}
        .header {{ text-align: center; color: white; margin-bottom: 30px; }}
        .header h1 {{ font-size: 2.5em; margin-bottom: 10px; }}
        .header p {{ opacity: 0.9; font-size: 1.1em; }}
        .tier-section {{ background: white; border-radius: 16px; padding: 30px; margin-bottom: 20px; box-shadow: 0 10px 30px rgba(0,0,0,0.1); }}
        .tier-title {{ font-size: 1.3em; font-weight: 600; margin-bottom: 20px; text-align: center; }}
        .tier-grid {{ display: grid; grid-template-columns: repeat(5, 1fr); gap: 12px; }}
        .tier-card {{ border: 3px solid #e0e0e0; border-radius: 12px; padding: 15px 10px; cursor: pointer; transition: all 0.3s; text-align: center; }}
        .tier-card:hover {{ transform: translateY(-3px); box-shadow: 0 5px 15px rgba(0,0,0,0.1); }}
        .tier-card.active {{ border-color: #667eea; background: linear-gradient(135deg, #667eea10 0%, #764ba210 100%); }}
        .tier-label {{ font-size: 2em; font-weight: bold; color: #667eea; margin-bottom: 8px; }}
        .tier-name {{ font-size: 0.95em; font-weight: 600; color: #333; }}
        .tier-budget {{ font-size: 1.1em; font-weight: bold; color: #e74c3c; margin: 5px 0; }}
        .tier-desc {{ font-size: 0.75em; color: #888; }}
        .generate-section {{ text-align: center; margin: 20px 0; }}
        .generate-btn {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; border: none; padding: 15px 60px; font-size: 1.2em; border-radius: 30px; cursor: pointer; }}
        .stats-section {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(160px, 1fr)); gap: 12px; margin-bottom: 20px; }}
        .stat-card {{ background: white; border-radius: 12px; padding: 15px; text-align: center; box-shadow: 0 5px 15px rgba(0,0,0,0.08); }}
        .stat-icon {{ font-size: 1.8em; margin-bottom: 8px; }}
        .stat-value {{ font-size: 1.5em; font-weight: bold; color: #667eea; }}
        .stat-label {{ font-size: 0.8em; color: #888; margin-top: 3px; }}
        .meal-plan {{ background: white; border-radius: 16px; padding: 30px; box-shadow: 0 10px 30px rgba(0,0,0,0.1); }}
        .plan-title {{ font-size: 1.5em; font-weight: 600; margin-bottom: 20px; text-align: center; color: #667eea; }}
        .days-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(350px, 1fr)); gap: 20px; }}
        .day-card {{ background: #f8f9fa; border-radius: 12px; overflow: hidden; }}
        .day-header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 15px 20px; font-weight: 600; display: flex; justify-content: space-between; }}
        .day-total {{ font-size: 0.9em; opacity: 0.9; }}
        .meal-slot {{ padding: 12px 20px; border-bottom: 1px solid #eee; }}
        .meal-slot:last-child {{ border-bottom: none; }}
        .meal-label {{ font-size: 0.85em; color: #888; margin-bottom: 6px; }}
        .meal-name {{ font-weight: 500; color: #333; font-size: 0.95em; }}
        .meal-info {{ display: flex; justify-content: space-between; margin-top: 4px; font-size: 0.8em; }}
        .meal-store {{ color: #888; }}
        .meal-price {{ color: #e74c3c; font-weight: 600; }}
        .tag {{ display: inline-block; padding: 1px 6px; border-radius: 8px; font-size: 0.65em; margin-left: 4px; vertical-align: middle; }}
        .tag-night {{ background: #9b59b6; color: white; }}
        .tag-fruit {{ background: #27ae60; color: white; }}
        .tag-coffee {{ background: #8B4513; color: white; }}
        @media (max-width: 768px) {{ .tier-grid {{ grid-template-columns: repeat(3, 1fr); }} .days-grid {{ grid-template-columns: 1fr; }} .header h1 {{ font-size: 1.8em; }} }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🍜 广软智能餐表生成器</h1>
            <p>Rust 实现 | 数据清洗 | 营业时间 | 荤素搭配 | 夜宵 | 水果 | 下午茶</p>
        </div>
        <div class="tier-section">
            <div class="tier-title">💰 选择你的资产等级</div>
            <div class="tier-grid">
                <div class="tier-card{}" data-tier="A1" onclick="location.href='?tier=A1'">
                    <div class="tier-label">A1</div><div class="tier-name">特困级</div>
                    <div class="tier-budget">¥12-18/天</div><div class="tier-desc">月 < 600元</div>
                </div>
                <div class="tier-card{}" data-tier="A2" onclick="location.href='?tier=A2'">
                    <div class="tier-label">A2</div><div class="tier-name">困难级</div>
                    <div class="tier-budget">¥18-26/天</div><div class="tier-desc">月 600-1000元</div>
                </div>
                <div class="tier-card{}" data-tier="A3" onclick="location.href='?tier=A3'">
                    <div class="tier-label">A3</div><div class="tier-name">普通级</div>
                    <div class="tier-budget">¥26-36/天</div><div class="tier-desc">月 1000-1500元</div>
                </div>
                <div class="tier-card{}" data-tier="A4" onclick="location.href='?tier=A4'">
                    <div class="tier-label">A4</div><div class="tier-name">小康级</div>
                    <div class="tier-budget">¥36-52/天</div><div class="tier-desc">月 1500-2200元</div>
                </div>
                <div class="tier-card{}" data-tier="A5" onclick="location.href='?tier=A5'">
                    <div class="tier-label">A5</div><div class="tier-name">富裕级</div>
                    <div class="tier-budget">¥52+/天</div><div class="tier-desc">月 > 2200元</div>
                </div>
            </div>
        </div>
        <div class="stats-section">
            <div class="stat-card"><div class="stat-icon">📊</div><div class="stat-value">¥{:.2}</div><div class="stat-label">本周合计</div></div>
            <div class="stat-card"><div class="stat-icon">📅</div><div class="stat-value">¥{:.2}</div><div class="stat-label">日均花费</div></div>
            <div class="stat-card"><div class="stat-icon">📆</div><div class="stat-value">¥{:.0}</div><div class="stat-label">月均花费</div></div>
            <div class="stat-card"><div class="stat-icon">☕</div><div class="stat-value">{}次</div><div class="stat-label">下午茶</div></div>
            <div class="stat-card"><div class="stat-icon">🌙</div><div class="stat-value">{}次</div><div class="stat-label">夜宵</div></div>
            <div class="stat-card"><div class="stat-icon">🍎</div><div class="stat-value">{}次</div><div class="stat-label">水果</div></div>
        </div>
        <div class="meal-plan">
            <div class="plan-title">📋 {} - 本周推荐餐表</div>
            <div class="days-grid">{}</div>
        </div>
    </div>
</body>
</html>"#,
        if tier_label == "A1" { " active" } else { "" },
        if tier_label == "A2" { " active" } else { "" },
        if tier_label == "A3" { " active" } else { "" },
        if tier_label == "A4" { " active" } else { "" },
        if tier_label == "A5" { " active" } else { "" },
        weekly_total, daily_avg, monthly_avg,
        coffee_count, night_count, fruit_count,
        tier_name, days_html
    )
}