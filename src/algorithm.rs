use rand::Rng;
use std::collections::HashSet;
use crate::data::*;

fn parse_business_hours(hours: &str) -> Vec<(f64, f64)> {
    if hours == "未设置" || hours.is_empty() {
        return vec![(0.0, 24.0)];
    }
    
    let mut periods = Vec::new();
    for part in hours.split(", ") {
        let times: Vec<&str> = part.split('-').collect();
        if times.len() == 2 {
            let start_parts: Vec<&str> = times[0].split(':').collect();
            let end_parts: Vec<&str> = times[1].split(':').collect();
            
            if start_parts.len() >= 2 && end_parts.len() >= 2 {
                let sh: f64 = start_parts[0].parse().unwrap_or(0.0);
                let sm: f64 = start_parts[1].parse().unwrap_or(0.0);
                let eh: f64 = end_parts[0].parse().unwrap_or(24.0);
                let em: f64 = end_parts[1].parse().unwrap_or(0.0);
                
                periods.push((sh + sm / 60.0, eh + em / 60.0));
            }
        }
    }
    
    if periods.is_empty() {
        vec![(0.0, 24.0)]
    } else {
        periods
    }
}

fn is_open_at(product: &Product, hour: f64) -> bool {
    let periods = parse_business_hours(&product.business_hours);
    periods.iter().any(|(start, end)| hour >= *start && hour < *end)
}

fn get_candidates<'a>(
    products: &'a [Product],
    meal_type: &str,
    price_range: (f64, f64),
    used: &HashSet<String>,
    hour: f64,
) -> Vec<&'a Product> {
    let (min_price, max_price) = price_range;
    
    products.iter().filter(|p| {
        if p.price < min_price || p.price > max_price * 1.3 {
            return false;
        }
        if !is_open_at(p, hour) {
            return false;
        }
        if used.contains(&p.name) {
            return false;
        }
        
        let cat = classify_product(p);
        match meal_type {
            "breakfast" => cat == "breakfast",
            "main" => cat == "main_meat" || cat == "main_veg",
            "drink" => cat == "drink",
            "night" => cat == "night" || (p.price <= 10.0 && (cat == "main_meat" || cat == "main_veg")),
            "fruit" => cat == "fruit",
            "coffee" => cat == "coffee" || cat == "drink",
            _ => true,
        }
    }).collect()
}

fn pick_meal<'a>(candidates: &[&'a Product], prefer_meat: bool) -> Option<&'a Product> {
    if candidates.is_empty() {
        return None;
    }
    
    let mut rng = rand::thread_rng();
    
    if prefer_meat {
        let meat: Vec<&&Product> = candidates.iter()
            .filter(|p| classify_product(p) == "main_meat")
            .collect();
        
        if !meat.is_empty() && rng.gen_range(0.0..1.0) > 0.4 {
            return Some(meat[rng.gen_range(0..meat.len())]);
        }
    }
    
    Some(candidates[rng.gen_range(0..candidates.len())])
}

pub fn generate_meal_plan(products: &[Product], tier: &Tier) -> Vec<DayMeal> {
    let days = ["周一", "周二", "周三", "周四", "周五", "周六", "周日"];
    let hours = (8.0, 12.0, 18.0, 22.0, 15.0, 14.0); // breakfast, lunch, dinner, night, coffee, fruit
    
    let mut rng = rand::thread_rng();
    let mut used = HashSet::new();
    let mut plan = Vec::new();
    
    for day in &days {
        // 早餐
        let breakfast_candidates = get_candidates(products, "breakfast", tier.breakfast, &used, hours.0);
        let breakfast = pick_meal(&breakfast_candidates, false);
        
        // 午餐
        let lunch_candidates = get_candidates(products, "main", tier.lunch, &used, hours.1);
        let lunch = pick_meal(&lunch_candidates, true);
        
        // 晚餐
        let dinner_candidates = get_candidates(products, "main", tier.dinner, &used, hours.2);
        let dinner = pick_meal(&dinner_candidates, true);
        
        let mut total = 0.0;
        
        if let Some(b) = breakfast {
            total += b.price;
            used.insert(b.name.clone());
        }
        if let Some(l) = lunch {
            total += l.price;
            used.insert(l.name.clone());
        }
        if let Some(d) = dinner {
            total += d.price;
            used.insert(d.name.clone());
        }
        
        // A4+ 午餐加饮品
        let mut lunch_display = lunch.map(|l| Meal {
            name: l.name.clone(),
            price: l.price,
            store: l.store.clone(),
            business_hours: l.business_hours.clone(),
            meal_type: MealType::Lunch,
        });
        
        if ["A4", "A5"].contains(&tier.name.split(' ').next().unwrap_or("")) {
            if let Some(l) = lunch {
                if total + 5.0 <= tier.daily_budget {
                    let drink_candidates = get_candidates(products, "drink", (3.0, 8.0), &HashSet::new(), hours.1);
                    if let Some(drink) = pick_meal(&drink_candidates, false) {
                        if total + drink.price <= tier.daily_budget {
                            lunch_display = Some(Meal {
                                name: format!("{} + {}", l.name, drink.name),
                                price: l.price + drink.price,
                                store: format!("{} / {}", l.store, drink.store),
                                business_hours: l.business_hours.clone(),
                                meal_type: MealType::Lunch,
                            });
                            total += drink.price;
                        }
                    }
                }
            }
        }
        
        // 下午茶
        let mut coffee = None;
        if tier.coffee && rng.gen_range(0.0..1.0) < tier.coffee_prob {
            let coffee_candidates = get_candidates(products, "coffee", tier.coffee_budget, &HashSet::new(), hours.4);
            if let Some(c) = pick_meal(&coffee_candidates, false) {
                if total + c.price <= tier.daily_budget * 1.1 {
                    total += c.price;
                    coffee = Some(Meal {
                        name: c.name.clone(),
                        price: c.price,
                        store: c.store.clone(),
                        business_hours: c.business_hours.clone(),
                        meal_type: MealType::Coffee,
                    });
                }
            }
        }
        
        // 夜宵
        let mut night_snack = None;
        if tier.night && rng.gen_range(0.0..1.0) < tier.night_prob {
            let night_candidates = get_candidates(products, "night", tier.night_budget, &HashSet::new(), hours.3);
            if let Some(n) = pick_meal(&night_candidates, true) {
                if total + n.price <= tier.daily_budget * 1.1 {
                    total += n.price;
                    night_snack = Some(Meal {
                        name: n.name.clone(),
                        price: n.price,
                        store: n.store.clone(),
                        business_hours: n.business_hours.clone(),
                        meal_type: MealType::NightSnack,
                    });
                }
            }
        }
        
        // 水果
        let mut fruit = None;
        if tier.fruit && dinner.is_some() && rng.gen_range(0.0..1.0) < tier.fruit_prob {
            let fruit_candidates = get_candidates(products, "fruit", tier.fruit_budget, &HashSet::new(), hours.5);
            if let Some(f) = pick_meal(&fruit_candidates, false) {
                if total + f.price <= tier.daily_budget * 1.1 {
                    total += f.price;
                    fruit = Some(Meal {
                        name: f.name.clone(),
                        price: f.price,
                        store: f.store.clone(),
                        business_hours: f.business_hours.clone(),
                        meal_type: MealType::Fruit,
                    });
                }
            }
        }
        
        plan.push(DayMeal {
            day: day.to_string(),
            breakfast: breakfast.map(|b| Meal {
                name: b.name.clone(),
                price: b.price,
                store: b.store.clone(),
                business_hours: b.business_hours.clone(),
                meal_type: MealType::Breakfast,
            }),
            lunch: lunch_display,
            dinner: dinner.map(|d| Meal {
                name: d.name.clone(),
                price: d.price,
                store: d.store.clone(),
                business_hours: d.business_hours.clone(),
                meal_type: MealType::Dinner,
            }),
            coffee,
            night_snack,
            fruit,
            total,
        });
    }
    
    plan
}