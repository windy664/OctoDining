use serde::{Deserialize, Serialize};
use std::collections::{hash_map::DefaultHasher, HashSet};
use std::hash::{Hash, Hasher};

#[derive(Clone, Debug, Deserialize, Serialize)]
pub struct Product {
    pub name: String,
    pub price: f64,
    pub store: String,
    pub category: String,
    pub business_hours: String,
}
impl Product {
    pub fn cents(&self) -> i64 {
        (self.price * 100.0).round() as i64
    }
}
#[cfg(test)]
fn sourced_by(products: &[Product], item: &Product) -> bool {
    if products
        .iter()
        .any(|p| p.name == item.name && p.store == item.store && p.cents() == item.cents())
    {
        return true;
    }
    let Some((left_name, right_name)) = item.name.split_once(" + ") else {
        return false;
    };
    products.iter().filter(|p| p.name == left_name).any(|left| {
        products
            .iter()
            .filter(|p| p.name == right_name)
            .any(|right| {
                format!("{} / {}", left.store, right.store) == item.store
                    && left.cents() + right.cents() == item.cents()
            })
    })
}
#[derive(Clone, Copy)]
pub struct Tier {
    pub name: &'static str,
    pub budget: i64,
    pub ranges: [(i64, i64); 3],
    pub coffee: bool,
    pub coffee_range: (i64, i64),
    pub coffee_prob: u8,
    pub night: bool,
    pub night_range: (i64, i64),
    pub night_prob: u8,
    pub fruit: bool,
    pub fruit_range: (i64, i64),
    pub fruit_prob: u8,
}
pub const TIERS: [Tier; 6] = [
    Tier {
        name: "A1 特困级",
        budget: 1500,
        ranges: [(200, 400), (400, 700), (400, 700)],
        coffee: false,
        coffee_range: (0, 0),
        coffee_prob: 0,
        night: false,
        night_range: (0, 0),
        night_prob: 0,
        fruit: true,
        fruit_range: (200, 500),
        fruit_prob: 20,
    },
    Tier {
        name: "A2 困难级",
        budget: 2200,
        ranges: [(300, 600), (600, 1000), (600, 1000)],
        coffee: false,
        coffee_range: (0, 0),
        coffee_prob: 0,
        night: false,
        night_range: (0, 0),
        night_prob: 0,
        fruit: true,
        fruit_range: (200, 500),
        fruit_prob: 30,
    },
    Tier {
        name: "A3 普通级",
        budget: 3200,
        ranges: [(500, 800), (800, 1400), (800, 1400)],
        coffee: true,
        coffee_range: (800, 1200),
        coffee_prob: 15,
        night: true,
        night_range: (300, 600),
        night_prob: 30,
        fruit: true,
        fruit_range: (200, 800),
        fruit_prob: 50,
    },
    Tier {
        name: "A4 小康级",
        budget: 4500,
        ranges: [(600, 1200), (1200, 2000), (1400, 2200)],
        coffee: true,
        coffee_range: (1000, 1500),
        coffee_prob: 40,
        night: true,
        night_range: (500, 1000),
        night_prob: 60,
        fruit: true,
        fruit_range: (200, 1000),
        fruit_prob: 70,
    },
    Tier {
        name: "A5 富裕级",
        budget: 6500,
        ranges: [(800, 1500), (1800, 2800), (2000, 3200)],
        coffee: true,
        coffee_range: (1200, 2000),
        coffee_prob: 60,
        night: true,
        night_range: (800, 1500),
        night_prob: 80,
        fruit: true,
        fruit_range: (200, 1500),
        fruit_prob: 90,
    },
    Tier {
        name: "A6 土豪级",
        budget: 10000,
        ranges: [(1000, 2200), (1500, 2200), (1500, 2200)],
        coffee: true,
        coffee_range: (1200, 2200),
        coffee_prob: 80,
        night: true,
        night_range: (1000, 1800),
        night_prob: 90,
        fruit: true,
        fruit_range: (200, 2000),
        fruit_prob: 100,
    },
];
pub const LABELS: [&str; 7] = [
    "早餐 · 08:00",
    "午餐 · 12:00",
    "晚餐 · 18:00",
    "下午茶 · 15:00",
    "夜宵 · 22:00",
    "水果 · 14:00",
    "午餐饮品 · 12:00",
];
const HOURS: [u16; 7] = [480, 720, 1080, 900, 1320, 840, 720];
#[derive(Clone, Debug, Serialize)]
pub struct Day {
    pub name: String,
    pub meals: Vec<Option<Product>>,
    pub notes: Vec<String>,
}
impl Day {
    pub fn total(&self) -> i64 {
        self.meals.iter().flatten().map(Product::cents).sum()
    }
}
pub fn load() -> Result<Vec<Product>, String> {
    let products: Vec<Product> =
        serde_json::from_str(include_str!("../products_clean.json")).map_err(|e| e.to_string())?;
    let products: Vec<_> = products
        .into_iter()
        .filter(|p| p.price.is_finite() && p.price >= 1.0 && !p.name.is_empty())
        .collect();
    if products.is_empty() {
        return Err("商品数据为空".into());
    }
    Ok(products)
}
fn minute(s: &str) -> Option<u16> {
    let (h, m) = s.trim().split_once(':')?;
    let (h, m) = (h.parse::<u16>().ok()?, m.parse::<u16>().ok()?);
    if h > 24 || m > 59 || (h == 24 && m != 0) {
        return None;
    }
    Some(h * 60 + m)
}
pub fn open_at(p: &Product, hour: u16) -> bool {
    // Unknown hours cannot establish availability. Snapshot is_open is not a weekly schedule.
    p.business_hours.replace('，', ",").split(',').any(|part| {
        let Some((a, b)) = part.trim().split_once('-') else {
            return false;
        };
        let (Some(a), Some(b)) = (minute(a), minute(b)) else {
            return false;
        };
        if a < b {
            hour >= a && hour < b
        } else if a > b {
            hour >= a || hour < b
        } else {
            false
        }
    })
}
fn contains(text: &str, words: &[&str]) -> bool {
    words.iter().any(|w| text.contains(w))
}
fn suitable(p: &Product, slot: usize) -> bool {
    let t = format!("{} {}", p.name, p.category);
    let coffee = contains(&t, &["咖啡", "美式", "拿铁", "摩卡", "卡布"]);
    let drink = coffee
        || contains(
            &t,
            &[
                "奶茶",
                "果茶",
                "果汁",
                "豆浆",
                "可乐",
                "柠檬茶",
                "饮料",
                "牛奶",
                "冰沙",
            ],
        );
    let fruit = p.store.contains("鲜果切") || p.category.contains("鲜果");
    match slot {
        0 => {
            !drink
                && !fruit
                && contains(
                    &t,
                    &[
                        "粥",
                        "包",
                        "小笼包",
                        "饼",
                        "肠粉",
                        "饺",
                        "馄饨",
                        "饭团",
                        "可颂",
                        "面",
                        "粉",
                        "馒头",
                    ],
                )
        }
        1 | 2 => {
            !drink
                && !fruit
                && contains(
                    &t,
                    &[
                        "饭", "面", "粉", "米线", "饺", "馄饨", "套餐", "汉堡", "拌", "双拼",
                        "三拼",
                    ],
                )
        }
        3 => coffee || drink,
        4 => {
            !drink
                && !fruit
                && contains(
                    &t,
                    &[
                        "烧烤",
                        "炸",
                        "烤",
                        "串",
                        "粥",
                        "粉",
                        "面",
                        "小吃",
                        "关东煮",
                        "卤",
                    ],
                )
        }
        5 => fruit,
        6 => drink && !coffee,
        _ => false,
    }
}
fn rank(seed: u64, day: usize, slot: usize, p: &Product) -> u64 {
    let mut h = DefaultHasher::new();
    (seed, day, slot, &p.name, &p.store).hash(&mut h);
    h.finish()
}
fn pick<'a>(
    products: &'a [Product],
    slot: usize,
    range: (i64, i64),
    hour: u16,
    seed: u64,
    day: usize,
    prefer_kfc: bool,
    meat_bias: bool,
) -> Option<&'a Product> {
    let mut items: Vec<_> = products
        .iter()
        .filter(|p| {
            suitable(p, slot) && open_at(p, hour) && p.cents() >= range.0 && p.cents() <= range.1
        })
        .collect();
    if items.is_empty() {
        return None;
    }
    items.sort_by_key(|p| {
        let text = format!("{} {}", p.name, p.store);
        let meat = contains(
            &text,
            &["鸡", "鸭", "猪", "牛", "羊", "排骨", "肉", "腿", "翅", "扒"],
        );
        let is_kfc = contains(
            &text,
            &[
                "肯德基",
                "炸鸡",
                "鸡腿",
                "鸡翅",
                "薯条",
                "可乐",
                "雪糕",
                "圣代",
            ],
        );
        (
            (prefer_kfc && !is_kfc),
            (!meat_bias || !meat),
            rank(seed, day, slot, p),
        )
    });
    items.into_iter().next()
}
pub fn generate(products: &[Product], tier_index: usize, seed: u64) -> Result<Vec<Day>, String> {
    let tier = TIERS.get(tier_index).ok_or("未知资产档次")?;
    if products.is_empty() {
        return Err("没有可用于规划的商品".into());
    }
    let mut plan = Vec::new();
    let mut used = HashSet::new();
    for (d, name) in ["周一", "周二", "周三", "周四", "周五", "周六", "周日"]
        .iter()
        .enumerate()
    {
        let roll = |slot: usize| (seed.wrapping_add(d as u64 * 67 + slot as u64 * 29) % 100) as u8;
        let mut day = Day {
            name: name.to_string(),
            meals: vec![None; 7],
            notes: vec![],
        };
        // Breakfast and main-meal price bands, with a 30% tolerance as in the original page.
        for slot in 0..3 {
            let range = tier.ranges[slot];
            let remaining = tier.budget - day.total();
            if remaining < range.0 {
                day.notes.push(format!(
                    "{}：剩余日预算不足以满足该餐次的最低价格区间",
                    LABELS[slot]
                ));
                continue;
            }
            let max = (range.1 * 130 / 100).min(remaining);
            let chosen = pick(
                products,
                slot,
                (range.0, max),
                HOURS[slot],
                seed,
                d,
                slot == 1 && d == 3 && roll(20) > 10,
                slot > 0 && roll(slot) < 60,
            );
            if let Some(p) = chosen {
                used.insert((p.name.clone(), p.store.clone()));
                day.meals[slot] = Some(p.clone());
            } else {
                day.notes.push(format!(
                    "{}：当前商品快照中没有符合价格和营业时段的餐品",
                    LABELS[slot]
                ));
            }
        }
        let mut total = day.total();
        // The source webpage adds a drink to A4-A6 lunch when budget permits.
        if tier_index >= 3 && day.meals[1].is_some() {
            let max = ((tier.budget - total - 500).min(800)).max(0);
            if max > 300 {
                if let Some(drink) = pick(products, 6, (300, max), HOURS[6], seed, d, false, false)
                {
                    if total + drink.cents() < tier.budget * 85 / 100 {
                        let old = day.meals[1].take().unwrap();
                        let mut combined = old.clone();
                        combined.name = format!("{} + {}", old.name, drink.name);
                        combined.store = format!("{} / {}", old.store, drink.store);
                        combined.price += drink.cents() as f64 / 100.0;
                        day.meals[1] = Some(combined);

                        total += drink.cents();
                    }
                }
            }
        }
        let is_a6 = tier_index == 5;
        let mut remaining = tier.budget - total;
        // Optional items follow the original page's per-tier likelihood and remaining-budget rules.
        if tier.coffee && remaining > if is_a6 { 800 } else { 1500 } && roll(3) < tier.coffee_prob {
            let cap = (remaining * (if is_a6 { 40 } else { 30 }) / 100).min(tier.coffee_range.1);
            if let Some(p) = pick(
                products,
                3,
                (tier.coffee_range.0, cap),
                HOURS[3],
                seed,
                d,
                false,
                false,
            ) {
                if total + p.cents() < tier.budget * (if is_a6 { 95 } else { 90 }) / 100 {
                    total += p.cents();
                    remaining -= p.cents();
                    day.meals[3] = Some(p.clone());
                }
            }
        }
        if tier.night && remaining > if is_a6 { 600 } else { 1200 } && roll(4) < tier.night_prob {
            let cap = (remaining * (if is_a6 { 50 } else { 40 }) / 100).min(tier.night_range.1);
            if let Some(p) = pick(
                products,
                4,
                (tier.night_range.0, cap),
                HOURS[4],
                seed,
                d,
                false,
                true,
            ) {
                if total + p.cents() <= tier.budget * (if is_a6 { 98 } else { 95 }) / 100 {
                    total += p.cents();
                    remaining -= p.cents();
                    day.meals[4] = Some(p.clone());
                }
            }
        }
        if tier.fruit
            && day.meals[2].is_some()
            && remaining > if is_a6 { 400 } else { 800 }
            && roll(5) < tier.fruit_prob
        {
            let cap = (remaining * (if is_a6 { 60 } else { 50 }) / 100).min(tier.fruit_range.1);
            if let Some(p) = pick(
                products,
                5,
                (tier.fruit_range.0, cap),
                HOURS[5],
                seed,
                d,
                false,
                false,
            ) {
                if total + p.cents() <= tier.budget * (if is_a6 { 98 } else { 95 }) / 100 {
                    day.meals[5] = Some(p.clone());
                }
            }
        }
        let _ = used;
        plan.push(day);
    }
    Ok(plan)
}
#[cfg(test)]
mod tests {
    use super::*;
    #[test]
    fn all_tiers_use_real_products_and_match_opening_hours() {
        let products = load().unwrap();
        for tier in 0..6 {
            for seed in 0..20 {
                let plan = generate(&products, tier, seed).unwrap();
                assert_eq!(plan.len(), 7);
                for day in plan {
                    assert!(
                        day.total() <= TIERS[tier].budget,
                        "daily budget exceeded: {}",
                        day.name
                    );
                    for (slot, meal) in day.meals.iter().enumerate() {
                        if let Some(p) = meal {
                            assert!(open_at(p, HOURS[slot]));
                            assert!(
                                sourced_by(&products, p),
                                "plan item is not in the source snapshot: {}",
                                p.name
                            );
                        }
                    }
                }
            }
        }
    }
    #[test]
    fn missing_data_is_explicit() {
        assert!(generate(&[], 0, 0).is_err());
        let p = Product {
            name: "无匹配商品".into(),
            price: 1.0,
            store: "测试".into(),
            category: "".into(),
            business_hours: "未设置".into(),
        };
        let plan = generate(&[p], 0, 0).unwrap();
        assert_eq!(plan[0].notes.len(), 3);
        assert_eq!(plan[0].total(), 0);
    }
    #[test]
    fn overnight_hours() {
        let mut p = load().unwrap().remove(0);
        p.business_hours = "22:00-02:00".into();
        assert!(open_at(&p, 23 * 60));
        assert!(open_at(&p, 60));
        assert!(!open_at(&p, 12 * 60));
    }
    #[test]
    fn regeneration_changes_the_plan() {
        let p = load().unwrap();
        assert_ne!(
            serde_json::to_string(&generate(&p, 2, 1).unwrap()).unwrap(),
            serde_json::to_string(&generate(&p, 2, 2).unwrap()).unwrap()
        );
    }
}
