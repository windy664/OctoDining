use serde::{Deserialize, Serialize};

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Product {
    pub name: String,
    pub price: f64,
    pub store: String,
    pub category: String,
    pub business_hours: String,
    pub is_open: bool,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Meal {
    pub name: String,
    pub price: f64,
    pub store: String,
    pub business_hours: String,
    pub meal_type: MealType,
}

#[derive(Debug, Clone, Serialize, Deserialize, PartialEq)]
pub enum MealType {
    Breakfast,
    Lunch,
    Dinner,
    Coffee,
    NightSnack,
    Fruit,
    Drink,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct DayMeal {
    pub day: String,
    pub breakfast: Option<Meal>,
    pub lunch: Option<Meal>,
    pub dinner: Option<Meal>,
    pub coffee: Option<Meal>,
    pub night_snack: Option<Meal>,
    pub fruit: Option<Meal>,
    pub total: f64,
}

#[derive(Debug, Clone)]
pub struct Tier {
    pub name: &'static str,
    pub daily_budget: f64,
    pub breakfast: (f64, f64),
    pub lunch: (f64, f64),
    pub dinner: (f64, f64),
    pub night: bool,
    pub night_budget: (f64, f64),
    pub night_prob: f64,
    pub fruit: bool,
    pub fruit_budget: (f64, f64),
    pub fruit_prob: f64,
    pub coffee: bool,
    pub coffee_budget: (f64, f64),
    pub coffee_prob: f64,
}

pub fn get_tiers() -> Vec<(&'static str, Tier)> {
    vec![
        ("A1", Tier {
            name: "A1 特困级",
            daily_budget: 15.0,
            breakfast: (2.0, 4.0),
            lunch: (4.0, 7.0),
            dinner: (4.0, 7.0),
            night: false,
            night_budget: (0.0, 0.0),
            night_prob: 0.0,
            fruit: false,
            fruit_budget: (0.0, 0.0),
            fruit_prob: 0.0,
            coffee: false,
            coffee_budget: (0.0, 0.0),
            coffee_prob: 0.0,
        }),
        ("A2", Tier {
            name: "A2 困难级",
            daily_budget: 22.0,
            breakfast: (3.0, 6.0),
            lunch: (6.0, 10.0),
            dinner: (6.0, 10.0),
            night: false,
            night_budget: (0.0, 0.0),
            night_prob: 0.0,
            fruit: false,
            fruit_budget: (0.0, 0.0),
            fruit_prob: 0.0,
            coffee: false,
            coffee_budget: (0.0, 0.0),
            coffee_prob: 0.0,
        }),
        ("A3", Tier {
            name: "A3 普通级",
            daily_budget: 32.0,
            breakfast: (5.0, 8.0),
            lunch: (8.0, 14.0),
            dinner: (8.0, 14.0),
            night: true,
            night_budget: (3.0, 6.0),
            night_prob: 0.3,
            fruit: true,
            fruit_budget: (3.0, 5.0),
            fruit_prob: 0.2,
            coffee: true,
            coffee_budget: (8.0, 12.0),
            coffee_prob: 0.15,
        }),
        ("A4", Tier {
            name: "A4 小康级",
            daily_budget: 45.0,
            breakfast: (6.0, 12.0),
            lunch: (12.0, 20.0),
            dinner: (14.0, 22.0),
            night: true,
            night_budget: (5.0, 10.0),
            night_prob: 0.6,
            fruit: true,
            fruit_budget: (5.0, 10.0),
            fruit_prob: 0.5,
            coffee: true,
            coffee_budget: (10.0, 15.0),
            coffee_prob: 0.4,
        }),
        ("A5", Tier {
            name: "A5 富裕级",
            daily_budget: 65.0,
            breakfast: (8.0, 15.0),
            lunch: (18.0, 28.0),
            dinner: (20.0, 32.0),
            night: true,
            night_budget: (8.0, 15.0),
            night_prob: 0.8,
            fruit: true,
            fruit_budget: (8.0, 15.0),
            fruit_prob: 0.7,
            coffee: true,
            coffee_budget: (12.0, 20.0),
            coffee_prob: 0.6,
        }),
    ]
}

#[derive(Debug, Deserialize)]
struct CsvRecord {
    #[serde(rename = "商品名称")]
    name: String,
    #[serde(rename = "价格")]
    price: String,
    #[serde(rename = "店铺名称")]
    store: String,
    #[serde(rename = "分类")]
    category: String,
    #[serde(rename = "营业时间")]
    business_hours: String,
    #[serde(rename = "是否营业中")]
    is_open: String,
    #[serde(rename = "是否缺货")]
    is_out_of_stock: String,
    #[serde(rename = "库存")]
    stock: String,
}

pub fn load_and_clean_csv(path: &str) -> anyhow::Result<Vec<Product>> {
    let mut rdr = csv::Reader::from_path(path)?;
    let mut products = Vec::new();

    for result in rdr.deserialize() {
        let record: CsvRecord = result?;
        
        let price: f64 = record.price.parse().unwrap_or(0.0);
        let stock: f64 = record.stock.parse().unwrap_or(0.0);
        let is_out = record.is_out_of_stock == "是";
        
        // 清洗规则
        if price < 1.0 || price > 100.0 {
            continue;
        }
        if stock <= 0.0 {
            continue;
        }
        if is_out {
            continue;
        }
        if record.name.contains("赠品") || record.name.contains("免费") {
            continue;
        }
        
        products.push(Product {
            name: record.name,
            price,
            store: record.store,
            category: record.category,
            business_hours: record.business_hours,
            is_open: record.is_open == "是",
        });
    }
    
    Ok(products)
}

pub fn classify_product(product: &Product) -> &'static str {
    let text = format!("{} {}", product.name, product.category);
    
    let breakfast_kw = ["粥", "包", "饼", "粉", "面", "肠粉", "饺子", "馄饨", "豆浆", "油条", "饭团", "卷", "可颂"];
    let main_kw = ["饭", "粉", "面", "米线", "馄饨", "饺子", "套餐", "堡", "卷", "炒", "盖饭", "拌饭", "焗饭"];
    let drink_kw = ["茶", "奶", "咖啡", "果汁", "冰沙", "饮", "柠", "椰", "美式", "拿铁"];
    let meat_kw = ["鸡", "鸭", "猪", "牛", "羊", "排骨", "肉", "腿", "翅", "扒"];
    let night_kw = ["烧烤", "炸", "烤", "串", "粥", "粉", "面", "小吃", "鸡", "鸭", "肠", "丸", "关东煮", "卤"];
    let fruit_kw = ["果", "瓜", "桃", "蕉", "橙", "柚", "莓", "提", "龙", "芒", "圣女"];
    let coffee_kw = ["咖啡", "美式", "拿铁", "卡布", "摩卡", "浓缩", "手冲", "生椰", "生酪"];
    
    let is_meat = meat_kw.iter().any(|k| text.contains(k));
    
    if breakfast_kw.iter().any(|k| text.contains(k)) {
        return "breakfast";
    }
    if coffee_kw.iter().any(|k| text.contains(k)) {
        return "coffee";
    }
    if drink_kw.iter().any(|k| text.contains(k)) {
        return "drink";
    }
    if fruit_kw.iter().any(|k| text.contains(k)) 
        && !["茶", "奶", "冰沙", "汁", "饮"].iter().any(|k| text.contains(k)) {
        return "fruit";
    }
    if night_kw.iter().any(|k| text.contains(k)) && product.price <= 15.0 {
        return "night";
    }
    if main_kw.iter().any(|k| text.contains(k)) {
        return if is_meat { "main_meat" } else { "main_veg" };
    }
    
    if is_meat { "main_meat" } else { "other" }
}