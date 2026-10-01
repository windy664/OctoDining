mod planner;
use eframe::egui::{self, Align, Color32, FontId, Layout, RichText, Stroke, TextureHandle, Vec2};
use planner::{Day, Product, TIERS};

const WHITE: Color32 = Color32::from_rgb(255, 255, 255);
const MUTED: Color32 = Color32::from_rgb(226, 232, 240);
const INDIGO: Color32 = Color32::from_rgb(99, 102, 241);
const PURPLE: Color32 = Color32::from_rgb(139, 92, 246);
fn money(cents: i64) -> String {
    format!("¥{:.2}", cents as f64 / 100.0)
}
fn glass() -> egui::Frame {
    egui::Frame::none()
        .fill(Color32::from_rgba_unmultiplied(22, 27, 48, 224))
        .stroke(Stroke::new(
            1.0_f32,
            Color32::from_rgba_unmultiplied(255, 255, 255, 52),
        ))
        .rounding(18.0)
        .inner_margin(18.0)
}
fn main() -> Result<(), eframe::Error> {
    if std::env::args().any(|a| a == "--verify-data") {
        let products = planner::load().expect("读取食堂商品数据");
        for i in 0..6 {
            let days = planner::generate(&products, i, 42).expect("生成餐表");
            println!(
                "{}：{} 个商品，七天合计 {}",
                TIERS[i].name,
                products.len(),
                money(days.iter().map(Day::total).sum())
            );
        }
        return Ok(());
    }
    eframe::run_native(
        "广软智能餐表生成器",
        eframe::NativeOptions {
            viewport: egui::ViewportBuilder::default()
                .with_inner_size([1200.0, 900.0])
                .with_min_inner_size([360.0, 640.0]),
            ..Default::default()
        },
        Box::new(|cc| {
            let mut fonts = egui::FontDefinitions::default();
            fonts.font_data.insert(
                "cjk".into(),
                egui::FontData::from_static(include_bytes!(
                    "../assets/fonts/DroidSansFallbackFull.ttf"
                )),
            );
            fonts
                .families
                .get_mut(&egui::FontFamily::Proportional)
                .unwrap()
                .push("cjk".into());
            cc.egui_ctx.set_fonts(fonts);
            let mut style = (*cc.egui_ctx.style()).clone();
            style.visuals = egui::Visuals::dark();
            style.visuals.panel_fill = Color32::TRANSPARENT;
            style.visuals.window_fill = Color32::TRANSPARENT;
            style.visuals.override_text_color = Some(WHITE);
            style.spacing.item_spacing = Vec2::new(12.0, 12.0);
            style
                .text_styles
                .insert(egui::TextStyle::Body, FontId::proportional(15.0));
            style
                .text_styles
                .insert(egui::TextStyle::Button, FontId::proportional(15.0));
            cc.egui_ctx.set_style(style);
            let decoder =
                png::Decoder::new(include_bytes!("../assets/meal-planner-bg.png").as_slice());
            let mut reader = decoder.read_info().expect("读取原网页背景图");
            let mut pixels = vec![0; reader.output_buffer_size()];
            let info = reader.next_frame(&mut pixels).expect("解码背景图");
            let image = egui::ColorImage::from_rgb(
                [info.width as usize, info.height as usize],
                &pixels[..info.buffer_size()],
            );
            let texture = cc.egui_ctx.load_texture(
                "original-meal-planner-bg",
                image,
                egui::TextureOptions::LINEAR,
            );
            let mut app = App::new(texture);
            if std::env::args().any(|a| a == "--preview") {
                app.generate();
            }
            Box::new(app)
        }),
    )
}
struct App {
    products: Vec<Product>,
    tier: usize,
    days: Vec<Day>,
    seed: u64,
    error: Option<String>,
    background: TextureHandle,
    capture_frames: u8,
}
impl App {
    fn new(background: TextureHandle) -> Self {
        let (products, error) = match planner::load() {
            Ok(p) => (p, None),
            Err(e) => (vec![], Some(e)),
        };
        Self {
            products,
            tier: 2,
            days: vec![],
            seed: std::time::SystemTime::now()
                .duration_since(std::time::UNIX_EPOCH)
                .unwrap_or_default()
                .as_nanos() as u64,
            error,
            background,
            capture_frames: 0,
        }
    }
    fn generate(&mut self) {
        self.seed = self.seed.wrapping_add(1);
        match planner::generate(&self.products, self.tier, self.seed) {
            Ok(days) => {
                self.days = days;
                self.error = None
            }
            Err(e) => self.error = Some(e),
        }
    }
    fn columns(width: f32) -> usize {
        if width < 480.0 {
            1
        } else if width < 768.0 {
            2
        } else if width < 1024.0 {
            3
        } else {
            6
        }
    }
    fn day_columns(width: f32) -> usize {
        if width < 768.0 {
            1
        } else if width < 1100.0 {
            2
        } else {
            3
        }
    }
    fn tier_grid(&mut self, ui: &mut egui::Ui) {
        let width = ui.available_width();
        let n = Self::columns(width);
        let descriptions = [
            "月生活费 < 600元 · 三餐温饱",
            "月生活费 600–1000元 · 三餐刚好",
            "月生活费 1000–1500元 · 偶尔夜宵/水果",
            "月生活费 1500–2200元 · 下午茶/夜宵",
            "月生活费 > 2200元 · 全部自由",
            "月生活费 > 3500元 · 想吃啥吃啥",
        ];
        let cell_w = (width - (n - 1) as f32 * 12.0) / n as f32;
        for row in (0..6).collect::<Vec<_>>().chunks(n) {
            ui.horizontal(|ui| {
                for &i in row {
                    let selected = self.tier == i;
                    let (min, max) = match i {
                        0 => ("12", "18"),
                        1 => ("18", "26"),
                        2 => ("26", "36"),
                        3 => ("36", "52"),
                        4 => ("52", "80"),
                        _ => ("100", "+"),
                    };
                    let fill = if selected {
                        Color32::from_rgba_unmultiplied(99, 102, 241, 95)
                    } else {
                        Color32::from_rgba_unmultiplied(255, 255, 255, 25)
                    };
                    let allocated = ui.allocate_ui_with_layout(
                        Vec2::new(cell_w, 165.0),
                        Layout::top_down(Align::Min),
                        |ui| {
                            let response = glass()
                                .fill(fill)
                                .stroke(Stroke::new(
                                    if selected { 2.0_f32 } else { 1.0_f32 },
                                    if selected {
                                        INDIGO
                                    } else {
                                        Color32::from_rgba_unmultiplied(255, 255, 255, 46)
                                    },
                                ))
                                .show(ui, |ui| {
                                    ui.set_min_width(ui.available_width());
                                    ui.set_min_height(133.0);
                                    ui.with_layout(
                                        Layout::top_down_justified(Align::Center),
                                        |ui| {
                                            ui.label(
                                                RichText::new(format!("A{}", i + 1))
                                                    .size(29.0)
                                                    .color(PURPLE)
                                                    .strong(),
                                            );
                                            ui.label(
                                                RichText::new(
                                                    TIERS[i]
                                                        .name
                                                        .split_once(' ')
                                                        .map(|x| x.1)
                                                        .unwrap_or(TIERS[i].name),
                                                )
                                                .strong()
                                                .size(16.0),
                                            );
                                            ui.label(
                                                RichText::new(format!("¥{}–{}/天", min, max))
                                                    .size(17.0)
                                                    .color(Color32::from_rgb(251, 191, 36))
                                                    .strong(),
                                            );
                                            ui.add_space(4.0);
                                            ui.label(
                                                RichText::new(descriptions[i])
                                                    .size(11.0)
                                                    .color(MUTED),
                                            );
                                        },
                                    );
                                });
                            response.response
                        },
                    );
                    if ui
                        .interact(
                            allocated.response.rect,
                            ui.make_persistent_id(("tier", i)),
                            egui::Sense::click(),
                        )
                        .clicked()
                    {
                        self.tier = i;
                    }
                }
            });
        }
    }
    fn stat_card(ui: &mut egui::Ui, icon: &str, value: String, label: &str, color: Color32) {
        glass().show(ui, |ui| {
            ui.set_min_width(ui.available_width());
            ui.with_layout(Layout::top_down_justified(Align::Center), |ui| {
                ui.label(RichText::new(icon).size(22.0).color(color));
                ui.label(RichText::new(value).size(23.0).strong().color(WHITE));
                ui.label(RichText::new(label).size(12.0).color(MUTED));
            });
        });
    }
    fn stats(&self, ui: &mut egui::Ui) {
        let total: i64 = self.days.iter().map(Day::total).sum();
        let values = [
            ("", money(total), "本周合计", INDIGO),
            ("", money(total / 7), "日均花费", PURPLE),
            ("", money(total * 30 / 7), "月均花费", INDIGO),
            (
                "",
                format!(
                    "{} 次",
                    self.days.iter().filter(|d| d.meals[3].is_some()).count()
                ),
                "下午茶",
                Color32::from_rgb(217, 119, 6),
            ),
            (
                "",
                format!(
                    "{} 次",
                    self.days.iter().filter(|d| d.meals[4].is_some()).count()
                ),
                "夜宵",
                PURPLE,
            ),
            (
                "",
                format!(
                    "{} 次",
                    self.days.iter().filter(|d| d.meals[5].is_some()).count()
                ),
                "水果",
                Color32::from_rgb(16, 185, 129),
            ),
        ];
        let n = Self::columns(ui.available_width());
        for row in (0..6).collect::<Vec<_>>().chunks(n) {
            let cell_w = (ui.available_width() - (row.len() - 1) as f32 * 12.0) / row.len() as f32;
            ui.horizontal(|ui| {
                for &i in row {
                    ui.allocate_ui_with_layout(
                        Vec2::new(cell_w, 92.0),
                        Layout::top_down(Align::Center),
                        |ui| {
                            Self::stat_card(
                                ui,
                                values[i].0,
                                values[i].1.clone(),
                                values[i].2,
                                values[i].3,
                            )
                        },
                    );
                }
            });
        }
    }
    fn day_card(ui: &mut egui::Ui, day: &Day) {
        glass().show(ui, |ui| {
            ui.set_min_width(ui.available_width());
            ui.horizontal(|ui| {
                ui.label(RichText::new(format!("{}", day.name)).size(17.0).strong());
                ui.with_layout(Layout::right_to_left(egui::Align::Center), |ui| {
                    ui.label(
                        RichText::new(money(day.total()))
                            .color(Color32::from_rgb(251, 191, 36))
                            .strong(),
                    );
                });
            });
            ui.add_space(5.0);
            for (slot, label, color) in [
                (0, "早餐 (8:00)", PURPLE),
                (1, "午餐 (12:00)", INDIGO),
                (2, "晚餐 (18:00)", PURPLE),
                (3, "下午茶 (15:00)", Color32::from_rgb(217, 119, 6)),
                (4, "夜宵 (22:00)", PURPLE),
                (5, "饭后水果", Color32::from_rgb(16, 185, 129)),
            ] {
                if let Some(p) = day.meals.get(slot).and_then(Option::as_ref) {
                    ui.add_space(5.0);
                    ui.separator();
                    ui.label(RichText::new(label).size(11.0).color(color));
                    ui.label(RichText::new(&p.name).size(14.0).strong());
                    ui.horizontal(|ui| {
                        ui.label(RichText::new(&p.store).size(10.0).color(MUTED));
                        ui.with_layout(Layout::right_to_left(egui::Align::Center), |ui| {
                            ui.label(
                                RichText::new(money(p.cents()))
                                    .size(12.0)
                                    .color(Color32::from_rgb(251, 191, 36)),
                            );
                        });
                    });
                }
            }
            for note in &day.notes {
                ui.colored_label(Color32::from_rgb(255, 198, 115), note);
            }
        });
    }
}
impl eframe::App for App {
    fn update(&mut self, ctx: &egui::Context, _frame: &mut eframe::Frame) {
        if std::env::args().any(|a| a == "--capture") {
            self.capture_frames = self.capture_frames.saturating_add(1);
            if self.capture_frames == 8 {
                ctx.send_viewport_cmd(egui::ViewportCommand::Screenshot);
            }
            ctx.input(|input| {
                for event in &input.events {
                    if let egui::Event::Screenshot { image, .. } = event {
                        let mut data =
                            format!("P6\n{} {}\n255\n", image.size[0], image.size[1]).into_bytes();
                        for px in &image.pixels {
                            data.extend_from_slice(&[px.r(), px.g(), px.b()]);
                        }
                        let _ = std::fs::write("/tmp/campus-meal-full.ppm", data);
                    }
                }
            });
            if self.capture_frames < 10 {
                ctx.request_repaint();
            }
        }
        let rect = ctx.screen_rect();
        let size = self.background.size_vec2();
        let scale = (rect.width() / size.x).max(rect.height() / size.y);
        let draw = size * scale;
        let bg_rect = egui::Rect::from_center_size(rect.center(), draw);
        let painter = ctx.layer_painter(egui::LayerId::background());
        painter.image(
            self.background.id(),
            bg_rect,
            egui::Rect::from_min_max(egui::Pos2::ZERO, egui::pos2(1.0, 1.0)),
            WHITE,
        );
        painter.rect_filled(rect, 0.0, Color32::from_black_alpha(153));
        egui::CentralPanel::default()
            .frame(
                egui::Frame::none()
                    .fill(Color32::TRANSPARENT)
                    .inner_margin(egui::Margin::symmetric(20.0, 12.0)),
            )
            .show(ctx, |ui| {
                egui::ScrollArea::vertical().show(ui, |ui| {
                    ui.set_max_width(1150.0);
                    ui.vertical_centered(|ui| {
                        ui.add_space(10.0);
                        ui.label(
                            RichText::new("广软智能餐表生成器")
                                .size(if ui.available_width() < 500.0 {
                                    28.0
                                } else {
                                    38.0
                                })
                                .strong()
                                .color(WHITE),
                        );
                    });
                    ui.add_space(14.0);
                    glass().show(ui, |ui| {
                        ui.set_min_width(ui.available_width());
                        ui.label(RichText::new("选择你的资产等级").size(21.0).strong());
                        ui.add_space(12.0);
                        self.tier_grid(ui);
                    });
                    ui.add_space(12.0);
                    ui.vertical_centered(|ui| {
                        let button = egui::Button::new(
                            RichText::new("一键生成餐表")
                                .size(19.0)
                                .strong()
                                .color(WHITE),
                        )
                        .fill(PURPLE)
                        .rounding(28.0)
                        .min_size(Vec2::new(280.0, 56.0));
                        if ui.add(button).clicked() {
                            self.generate();
                        }
                    });
                    if let Some(error) = &self.error {
                        ui.colored_label(Color32::LIGHT_RED, error);
                    }
                    if !self.days.is_empty() {
                        ui.add_space(6.0);
                        self.stats(ui);
                        ui.add_space(3.0);
                        glass().show(ui, |ui| {
                            ui.set_min_width(ui.available_width());
                            ui.label(
                                RichText::new(format!("{} - 本周推荐餐表", TIERS[self.tier].name))
                                    .size(23.0)
                                    .strong(),
                            );
                        });
                        let n = Self::day_columns(ui.available_width());
                        for row in (0..7).collect::<Vec<_>>().chunks(n) {
                            ui.horizontal(|ui| {
                                for &i in row {
                                    ui.allocate_ui_with_layout(
                                        Vec2::new(
                                            (ui.available_width() - (row.len() - 1) as f32 * 12.0)
                                                / row.len() as f32,
                                            0.0,
                                        ),
                                        Layout::top_down(Align::Min),
                                        |ui| Self::day_card(ui, &self.days[i]),
                                    );
                                }
                            });
                        }
                    }
                    ui.add_space(20.0);
                    ui.vertical_centered(|ui| {
                        ui.label(
                            RichText::new(format!(
                                "基于广州软件学院食堂商品数据 · {} 条真实商品",
                                self.products.len()
                            ))
                            .small()
                            .color(MUTED),
                        )
                    });
                });
            });
    }
}
