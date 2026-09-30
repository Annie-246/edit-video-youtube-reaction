import React from "react";
import { interpolate, spring, useCurrentFrame, useVideoConfig } from "remotion";
import { Particles } from "../library/motion";

/**
 * 4 Motion Graphic Standards derived from mau-graphic-motion-1..4
 * All templates support dynamic theme accents, flexible scales,
 * and work for both compact corner panels (900x478) and full-frame cards (1920x1080).
 */

// ─────────────────────────────────────────────────────────────
// MẪU 1: Cột tăng trưởng bậc thang (Tương ứng mau-graphic-motion-1)
// ─────────────────────────────────────────────────────────────
export const BarGrowth: React.FC<{
  accent?: string;
  bars?: number[];
  kicker?: string;
  headline?: string;
  width?: number;
  height?: number;
}> = ({
  accent = "#38BDF8",
  bars = [28, 42, 60, 80, 110, 150, 185],
  kicker,
  headline,
  width = 600,
  height = 320,
}) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const maxVal = Math.max(...bars);
  const barWidth = Math.min(48, Math.floor((width * 0.75) / bars.length));
  const gap = 14;

  return (
    <div
      style={{
        position: "relative",
        width: "100%",
        height: "100%",
        display: "flex",
        flexDirection: "column",
        justifyContent: "center",
        alignItems: "center",
      }}
    >
      <Particles count={25} />
      {kicker && (
        <div
          style={{
            fontSize: 16,
            fontWeight: 700,
            letterSpacing: 3,
            color: accent,
            textTransform: "uppercase",
            marginBottom: 6,
          }}
        >
          {kicker}
        </div>
      )}
      {headline && (
        <div
          style={{
            fontSize: 26,
            fontWeight: 700,
            color: "#FFFFFF",
            marginBottom: 20,
            textAlign: "center",
          }}
        >
          {headline}
        </div>
      )}

      {/* Biểu đồ cột bo tròn phát sáng */}
      <div
        style={{
          display: "flex",
          alignItems: "flex-end",
          justifyContent: "center",
          gap: `${gap}px`,
          height: `${height * 0.7}px`,
          paddingBottom: 10,
          borderBottom: "2px solid rgba(255, 255, 255, 0.25)",
        }}
      >
        {bars.map((val, idx) => {
          const delay = idx * 4;
          const spr = spring({
            frame: Math.max(0, frame - delay),
            fps,
            config: { damping: 14, stiffness: 90 },
          });
          const targetH = (val / maxVal) * (height * 0.65);
          const currentH = targetH * spr;
          const isHighest = idx === bars.length - 1;

          return (
            <div
              key={idx}
              style={{
                width: `${barWidth}px`,
                height: `${currentH}px`,
                background: isHighest
                  ? `linear-gradient(180deg, #FFFFFF 0%, ${accent} 100%)`
                  : "rgba(255, 255, 255, 0.9)",
                borderRadius: `${barWidth / 2}px`,
                boxShadow: isHighest
                  ? `0 0 24px ${accent}AA`
                  : "0 0 12px rgba(255, 255, 255, 0.3)",
                transition: "height 0.1s ease",
              }}
            />
          );
        })}
      </div>
    </div>
  );
};

// ─────────────────────────────────────────────────────────────
// MẪU 2: So sánh 2 đường xu hướng (Tương ứng mau-graphic-motion-2)
// ─────────────────────────────────────────────────────────────
export const DualLineTrend: React.FC<{
  accent?: string;
  points1?: number[];
  points2?: number[];
  label1?: string;
  label2?: string;
  kicker?: string;
  headline?: string;
  width?: number;
  height?: number;
}> = ({
  accent = "#38BDF8",
  points1 = [15, 24, 45, 70, 95, 125],
  points2 = [10, 18, 30, 55, 80, 105],
  label1 = "Tăng trưởng AI",
  label2 = "Tiêu chuẩn",
  kicker,
  headline,
  width = 620,
  height = 300,
}) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const progress = interpolate(frame, [8, fps * 1.8], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  const maxVal = Math.max(...points1, ...points2);
  const W = width * 0.85;
  const H = height * 0.6;

  const toSvgCoords = (pts: number[]) =>
    pts.map((v, i) => {
      const x = (i / (pts.length - 1)) * W;
      const y = H - (v / maxVal) * H;
      return { x, y, str: `${x.toFixed(1)},${y.toFixed(1)}` };
    });

  const coords1 = toSvgCoords(points1);
  const coords2 = toSvgCoords(points2);
  const lineLength = 1600;

  return (
    <div
      style={{
        position: "relative",
        width: "100%",
        height: "100%",
        display: "flex",
        flexDirection: "column",
        justifyContent: "center",
        alignItems: "center",
      }}
    >
      <Particles count={25} />
      {kicker && (
        <div
          style={{
            fontSize: 16,
            fontWeight: 700,
            letterSpacing: 3,
            color: accent,
            textTransform: "uppercase",
            marginBottom: 6,
          }}
        >
          {kicker}
        </div>
      )}
      {headline && (
        <div
          style={{
            fontSize: 26,
            fontWeight: 700,
            color: "#FFFFFF",
            marginBottom: 16,
            textAlign: "center",
          }}
        >
          {headline}
        </div>
      )}

      {/* Chart Canvas */}
      <div style={{ position: "relative", width: `${W}px`, height: `${H}px` }}>
        <svg width={W} height={H} style={{ overflow: "visible" }}>
          {/* Lưới ngang mờ */}
          {[0, 0.33, 0.66, 1].map((lvl, idx) => (
            <line
              key={idx}
              x1={0}
              x2={W}
              y1={H * lvl}
              y2={H * lvl}
              stroke="rgba(255, 255, 255, 0.15)"
              strokeWidth={1}
            />
          ))}

          {/* Đường 2 (Trắng) */}
          <polyline
            points={coords2.map((p) => p.str).join(" ")}
            fill="none"
            stroke="#FFFFFF"
            strokeWidth={4}
            strokeLinecap="round"
            strokeDasharray={lineLength}
            strokeDashoffset={lineLength * (1 - progress)}
            style={{ opacity: 0.85 }}
          />

          {/* Đường 1 (Neon Accent) */}
          <polyline
            points={coords1.map((p) => p.str).join(" ")}
            fill="none"
            stroke={accent}
            strokeWidth={5}
            strokeLinecap="round"
            strokeDasharray={lineLength}
            strokeDashoffset={lineLength * (1 - progress)}
            filter="drop-shadow(0 0 8px currentColor)"
          />

          {/* Các điểm nút (Keyframe dots) */}
          {coords1.map((p, idx) => {
            const dotOpacity = interpolate(
              progress,
              [(idx - 0.5) / coords1.length, idx / coords1.length],
              [0, 1],
              { extrapolateLeft: "clamp", extrapolateRight: "clamp" }
            );
            return (
              <circle
                key={`c1-${idx}`}
                cx={p.x}
                cy={p.y}
                r={5}
                fill={accent}
                stroke="#FFFFFF"
                strokeWidth={2}
                opacity={dotOpacity}
              />
            );
          })}
        </svg>

        {/* Chú thích 2 đường */}
        <div
          style={{
            display: "flex",
            justifyContent: "center",
            gap: 24,
            marginTop: 18,
          }}
        >
          <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
            <span
              style={{
                width: 12,
                height: 12,
                borderRadius: "50%",
                background: accent,
                boxShadow: `0 0 8px ${accent}`,
              }}
            />
            <span style={{ fontSize: 15, color: "#FFFFFF", fontWeight: 600 }}>
              {label1}
            </span>
          </div>
          <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
            <span
              style={{
                width: 12,
                height: 12,
                borderRadius: "50%",
                background: "#FFFFFF",
              }}
            />
            <span style={{ fontSize: 15, color: "rgba(255,255,255,0.7)", fontWeight: 500 }}>
              {label2}
            </span>
          </div>
        </div>
      </div>
    </div>
  );
};

// ─────────────────────────────────────────────────────────────
// MẪU 3: Dashboard Trình duyệt & Luồng xử lý AI (Tương ứng mau-graphic-motion-3)
// ─────────────────────────────────────────────────────────────
export const BrowserAIFlow: React.FC<{
  accent?: string;
  kicker?: string;
  headline?: string;
  metricLabel?: string;
}> = ({
  accent = "#F43F5E",
  kicker,
  headline,
  metricLabel = "Tự động phân tích",
}) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const winSpr = spring({ frame, fps, config: { damping: 16 } });
  const checkSpr = spring({
    frame: Math.max(0, frame - 28),
    fps,
    config: { damping: 12 },
  });

  return (
    <div
      style={{
        position: "relative",
        width: "100%",
        height: "100%",
        display: "flex",
        flexDirection: "column",
        justifyContent: "center",
        alignItems: "center",
      }}
    >
      <Particles count={25} />
      {kicker && (
        <div
          style={{
            fontSize: 16,
            fontWeight: 700,
            letterSpacing: 3,
            color: "#38BDF8",
            textTransform: "uppercase",
            marginBottom: 6,
          }}
        >
          {kicker}
        </div>
      )}
      {headline && (
        <div
          style={{
            fontSize: 24,
            fontWeight: 700,
            color: "#FFFFFF",
            marginBottom: 16,
            textAlign: "center",
          }}
        >
          {headline}
        </div>
      )}

      <div
        style={{
          display: "flex",
          gap: 20,
          alignItems: "center",
          justifyContent: "center",
          width: "90%",
          transform: `scale(${winSpr})`,
        }}
      >
        {/* Khung trình duyệt bên trái */}
        <div
          style={{
            flex: 1.3,
            background: "rgba(15, 23, 42, 0.75)",
            border: "1px solid rgba(255, 255, 255, 0.15)",
            borderRadius: 14,
            overflow: "hidden",
            boxShadow: "0 16px 32px rgba(0,0,0,0.5)",
          }}
        >
          {/* Header 3 chấm macOS */}
          <div
            style={{
              display: "flex",
              alignItems: "center",
              gap: 6,
              padding: "10px 14px",
              background: "rgba(30, 41, 59, 0.6)",
              borderBottom: "1px solid rgba(255, 255, 255, 0.08)",
            }}
          >
            <span style={{ width: 10, height: 10, borderRadius: "50%", background: "#EF4444" }} />
            <span style={{ width: 10, height: 10, borderRadius: "50%", background: "#F59E0B" }} />
            <span style={{ width: 10, height: 10, borderRadius: "50%", background: "#10B981" }} />
          </div>

          {/* Sóng đồ thị trong trình duyệt */}
          <div style={{ padding: "14px" }}>
            <svg width="100%" height="80" viewBox="0 0 320 80">
              <path
                d="M 10 50 Q 50 30, 90 45 T 170 30 T 250 50 T 310 20"
                fill="none"
                stroke={accent}
                strokeWidth={3.5}
                filter="drop-shadow(0 0 6px currentColor)"
              />
              {[
                { cx: 10, cy: 50 },
                { cx: 90, cy: 45 },
                { cx: 170, cy: 30 },
                { cx: 250, cy: 50 },
                { cx: 310, cy: 20 },
              ].map((p, i) => (
                <circle key={i} cx={p.cx} cy={p.cy} r={4} fill="#FFFFFF" />
              ))}
            </svg>

            {/* 4 Thẻ chỉ số con */}
            <div style={{ display: "grid", gridTemplateColumns: "repeat(4, 1fr)", gap: 6, marginTop: 8 }}>
              {[0, 1, 2, 3].map((idx) => {
                const highlighted = idx === 1;
                return (
                  <div
                    key={idx}
                    style={{
                      height: 38,
                      borderRadius: 6,
                      background: highlighted ? "rgba(245, 158, 11, 0.2)" : "rgba(255,255,255,0.05)",
                      border: highlighted ? "1.5px solid #F59E0B" : "1px solid rgba(255,255,255,0.08)",
                      boxShadow: highlighted ? "0 0 10px rgba(245, 158, 11, 0.4)" : "none",
                    }}
                  />
                );
              })}
            </div>
          </div>
        </div>

        {/* Khung quy trình AI bên phải */}
        <div
          style={{
            flex: 1,
            background: "rgba(15, 23, 42, 0.75)",
            border: "1px solid rgba(255, 255, 255, 0.15)",
            borderRadius: 14,
            padding: 16,
            display: "flex",
            flexDirection: "column",
            alignItems: "center",
            boxShadow: "0 16px 32px rgba(0,0,0,0.5)",
          }}
        >
          <div
            style={{
              padding: "4px 12px",
              borderRadius: 6,
              background: "#38BDF8",
              color: "#0F172A",
              fontSize: 13,
              fontWeight: 800,
              marginBottom: 14,
            }}
          >
            AI SYSTEM
          </div>

          {/* Dòng mô phỏng text */}
          <div style={{ width: "100%", display: "flex", flexDirection: "column", gap: 7 }}>
            <div style={{ height: 6, background: "rgba(255,255,255,0.25)", borderRadius: 3, width: "95%" }} />
            <div style={{ height: 6, background: "rgba(255,255,255,0.2)", borderRadius: 3, width: "80%" }} />
            <div style={{ height: 6, background: "rgba(255,255,255,0.2)", borderRadius: 3, width: "90%" }} />
          </div>

          {/* Vòng checkmark xanh lá phát sáng */}
          <div
            style={{
              marginTop: 16,
              width: 52,
              height: 52,
              borderRadius: "50%",
              border: "3px solid #10B981",
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              color: "#10B981",
              fontSize: 26,
              fontWeight: 900,
              boxShadow: "0 0 16px #10B98188",
              transform: `scale(${checkSpr})`,
            }}
          >
            ✓
          </div>
        </div>
      </div>
    </div>
  );
};

// ─────────────────────────────────────────────────────────────
// MẪU 4: Đồng hồ chu kỳ & Tác vụ xoay quanh (Tương ứng mau-graphic-motion-4)
// ─────────────────────────────────────────────────────────────
export const ClockCycleTasks: React.FC<{
  accent?: string;
  kicker?: string;
  headline?: string;
  taskCount?: number;
}> = ({
  accent = "#38BDF8",
  kicker,
  headline = "Quy trình tối ưu 24/7",
  taskCount = 7,
}) => {
  const frame = useCurrentFrame();

  const minuteHandAngle = (frame * 6) % 360;
  const hourHandAngle = (frame * 1.5) % 360;

  return (
    <div
      style={{
        position: "relative",
        width: "100%",
        height: "100%",
        display: "flex",
        flexDirection: "column",
        justifyContent: "center",
        alignItems: "center",
      }}
    >
      <Particles count={25} />
      {kicker && (
        <div
          style={{
            fontSize: 16,
            fontWeight: 700,
            letterSpacing: 3,
            color: accent,
            textTransform: "uppercase",
            marginBottom: 6,
          }}
        >
          {kicker}
        </div>
      )}
      {headline && (
        <div
          style={{
            fontSize: 24,
            fontWeight: 700,
            color: "#FFFFFF",
            marginBottom: 10,
            textAlign: "center",
          }}
        >
          {headline}
        </div>
      )}

      {/* Mặt đồng hồ trung tâm & Các quỹ đạo */}
      <div
        style={{
          position: "relative",
          width: 260,
          height: 260,
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
        }}
      >
        {/* Vòng quỹ đạo ngoài */}
        <div
          style={{
            position: "absolute",
            width: 250,
            height: 250,
            borderRadius: "50%",
            border: "1px dashed rgba(56, 189, 248, 0.3)",
          }}
        />
        {/* Vòng quỹ đạo giữa */}
        <div
          style={{
            position: "absolute",
            width: 200,
            height: 200,
            borderRadius: "50%",
            border: "1px solid rgba(255, 255, 255, 0.15)",
          }}
        />

        {/* Khung mặt đồng hồ */}
        <div
          style={{
            position: "relative",
            width: 140,
            height: 140,
            borderRadius: "50%",
            background: "rgba(15, 23, 42, 0.9)",
            border: `3px solid ${accent}`,
            boxShadow: `0 0 20px ${accent}66`,
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
          }}
        >
          {/* Trục kim đồng hồ */}
          <div
            style={{
              position: "absolute",
              width: 8,
              height: 8,
              borderRadius: "50%",
              background: "#FFFFFF",
              zIndex: 10,
            }}
          />

          {/* Kim giờ */}
          <div
            style={{
              position: "absolute",
              width: 3.5,
              height: 35,
              background: "#FFFFFF",
              borderRadius: 2,
              top: 35,
              left: 68,
              transformOrigin: "bottom center",
              transform: `rotate(${hourHandAngle}deg)`,
            }}
          />

          {/* Kim phút */}
          <div
            style={{
              position: "absolute",
              width: 2.5,
              height: 50,
              background: accent,
              borderRadius: 2,
              top: 20,
              left: 68.5,
              transformOrigin: "bottom center",
              transform: `rotate(${minuteHandAngle}deg)`,
              boxShadow: `0 0 6px ${accent}`,
            }}
          />
        </div>

        {/* Các thẻ tác vụ vệ tinh xoay quanh */}
        {new Array(taskCount).fill(0).map((_, i) => {
          const angle = (i * 360) / taskCount - 90;
          const rad = (angle * Math.PI) / 180;
          const radius = 100;
          const cx = Math.cos(rad) * radius;
          const cy = Math.sin(rad) * radius;

          return (
            <div
              key={i}
              style={{
                position: "absolute",
                transform: `translate(${cx}px, ${cy}px)`,
                width: 34,
                height: 24,
                borderRadius: 6,
                background: "rgba(30, 41, 59, 0.85)",
                border: "1.5px solid rgba(56, 189, 248, 0.6)",
                display: "flex",
                flexDirection: "column",
                justifyContent: "center",
                alignItems: "center",
                gap: 2.5,
                boxShadow: "0 0 10px rgba(56, 189, 248, 0.25)",
              }}
            >
              <div style={{ width: 18, height: 2, background: "#FFFFFF", borderRadius: 1 }} />
              <div style={{ width: 14, height: 2, background: "rgba(255,255,255,0.6)", borderRadius: 1 }} />
              <div style={{ width: 10, height: 2, background: "rgba(255,255,255,0.4)", borderRadius: 1 }} />
            </div>
          );
        })}
      </div>
    </div>
  );
};

// ─────────────────────────────────────────────────────────────
// MẪU 5: Bảng so sánh 3 loại Token (Input, Output, Cache Read)
// ─────────────────────────────────────────────────────────────
export const TokenComparisonTable: React.FC<{
  accent?: string;
  kicker?: string;
  headline?: string;
}> = ({
  accent = "#8B7CFF",
  kicker = "CƠ CHẾ GIÁ ANTHROPIC",
  headline = "So sánh 3 loại Token khi dùng Claude",
}) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const cols = [
    {
      title: "Input Token",
      tag: "DỮ LIỆU ĐẦU VÀO",
      tagBg: "rgba(59, 130, 246, 0.2)",
      tagBorder: "#3B82F6",
      desc: "Prompt, lịch sử chat, system prompt, CLAUDE.md và danh sách tool.",
      price: "$5.00",
      unit: "trên 1 triệu token (Opus 5.5)",
      note: "Xử lý mỗi lượt",
      highlight: false,
    },
    {
      title: "Output Token",
      tag: "KẾT QUẢ SINH RA",
      tagBg: "rgba(239, 68, 68, 0.2)",
      tagBorder: "#EF4444",
      desc: "Câu trả lời Claude tự tư duy và sinh ra từng chữ một.",
      price: "$20.00",
      unit: "trên 1 triệu token (Đắt gấp 4 lần!)",
      note: "Chi phí cao nhất",
      highlight: false,
    },
    {
      title: "Cache Read",
      tag: "ĐỌC LẠI TỪ CACHE",
      tagBg: "rgba(16, 185, 129, 0.25)",
      tagBorder: "#10B981",
      desc: "Tận dụng lại context cũ không đổi, Claude chỉ đọc lại mà không tính toán lại.",
      price: "$0.50",
      unit: "chỉ bằng 1/10 giá Input thông thường",
      note: "⚡ Tiết kiệm tới 90%",
      highlight: true,
    },
  ];

  return (
    <div
      style={{
        position: "relative",
        width: "100%",
        height: "100%",
        display: "flex",
        flexDirection: "column",
        justifyContent: "center",
        alignItems: "center",
        padding: "0 40px",
      }}
    >
      <Particles count={30} />
      {kicker && (
        <div
          style={{
            fontSize: 16,
            fontWeight: 700,
            letterSpacing: 3,
            color: accent,
            textTransform: "uppercase",
            marginBottom: 8,
          }}
        >
          {kicker}
        </div>
      )}
      {headline && (
        <div
          style={{
            fontSize: 28,
            fontWeight: 700,
            color: "#FFFFFF",
            marginBottom: 24,
            textAlign: "center",
          }}
        >
          {headline}
        </div>
      )}

      <div
        style={{
          display: "grid",
          gridTemplateColumns: "repeat(3, 1fr)",
          gap: 20,
          width: "100%",
          maxWidth: 1200,
        }}
      >
        {cols.map((col, idx) => {
          const spr = spring({
            frame: Math.max(0, frame - idx * 6),
            fps,
            config: { damping: 14, stiffness: 80 },
          });

          return (
            <div
              key={idx}
              style={{
                background: col.highlight ? "rgba(16, 185, 129, 0.08)" : "rgba(30, 41, 59, 0.65)",
                border: col.highlight ? "2px solid #10B981" : "1px solid rgba(255, 255, 255, 0.15)",
                borderRadius: 16,
                padding: "24px 20px",
                display: "flex",
                flexDirection: "column",
                boxShadow: col.highlight ? "0 0 25px rgba(16, 185, 129, 0.3)" : "0 10px 24px rgba(0,0,0,0.4)",
                transform: `scale(${spr})`,
                backdropFilter: "blur(12px)",
              }}
            >
              <div
                style={{
                  alignSelf: "flex-start",
                  fontSize: 11,
                  fontWeight: 800,
                  letterSpacing: 1,
                  padding: "4px 10px",
                  borderRadius: 6,
                  background: col.tagBg,
                  color: col.tagBorder,
                  border: `1px solid ${col.tagBorder}`,
                  marginBottom: 12,
                }}
              >
                {col.tag}
              </div>

              <div style={{ fontSize: 22, fontWeight: 700, color: "#FFFFFF", marginBottom: 8 }}>
                {col.title}
              </div>

              <div style={{ fontSize: 13, color: "rgba(255,255,255,0.7)", lineHeight: 1.45, minHeight: 56, marginBottom: 16 }}>
                {col.desc}
              </div>

              <div style={{ marginTop: "auto", borderTop: "1px solid rgba(255,255,255,0.1)", paddingTop: 14 }}>
                <div style={{ fontSize: 32, fontWeight: 800, color: col.highlight ? "#10B981" : "#FFFFFF" }}>
                  {col.price}
                </div>
                <div style={{ fontSize: 12, color: "rgba(255,255,255,0.6)", marginTop: 2 }}>
                  {col.unit}
                </div>
                <div
                  style={{
                    marginTop: 10,
                    fontSize: 12,
                    fontWeight: 700,
                    color: col.highlight ? "#10B981" : accent,
                  }}
                >
                  {col.note}
                </div>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};

// ─────────────────────────────────────────────────────────────
// MẪU 6: Vai trò 4 Model Anthropic như nhân viên công ty
// ─────────────────────────────────────────────────────────────
export const AnthropicModelRoles: React.FC<{
  accent?: string;
  kicker?: string;
  headline?: string;
}> = ({
  accent = "#8B7CFF",
  kicker = "HỆ SINH THÁI ANTHROPIC",
  headline = "4 Model như 4 vị trí nhân sự trong phòng làm việc",
}) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const models = [
    {
      name: "Haiku 4.5",
      role: "Trợ lý siêu tốc",
      icon: "⚡",
      badgeColor: "#38BDF8",
      strengths: "Lọc thông tin, đọc log, chạy subagent, phản hồi tức thì với chi phí tối thiểu.",
    },
    {
      name: "Sonnet 5",
      role: "Nhân viên tháo vát",
      icon: "🎯",
      badgeColor: "#10B981",
      strengths: "Cân bằng hoàn hảo giữa thông minh và tốc độ. Xử lý 90% công việc lập trình & content.",
    },
    {
      name: "Opus 5.5",
      role: "Chuyên gia đầu ngành",
      icon: "🧠",
      badgeColor: "#F59E0B",
      strengths: "Khả năng suy luận đỉnh cao, giải quyết bài toán phức tạp, thiết kế kiến trúc chuẩn.",
    },
    {
      name: "Fable 5.1",
      role: "Quản lý dự án dài hơi",
      icon: "🏛️",
      badgeColor: "#EC4899",
      strengths: "Tự chủ cao, bền bỉ qua hàng chục vòng thử thách, giải quyết các mục tiêu chiến lược.",
    },
  ];

  return (
    <div
      style={{
        position: "relative",
        width: "100%",
        height: "100%",
        display: "flex",
        flexDirection: "column",
        justifyContent: "center",
        alignItems: "center",
        padding: "0 40px",
      }}
    >
      <Particles count={30} />
      {kicker && (
        <div
          style={{
            fontSize: 16,
            fontWeight: 700,
            letterSpacing: 3,
            color: accent,
            textTransform: "uppercase",
            marginBottom: 8,
          }}
        >
          {kicker}
        </div>
      )}
      {headline && (
        <div
          style={{
            fontSize: 28,
            fontWeight: 700,
            color: "#FFFFFF",
            marginBottom: 24,
            textAlign: "center",
          }}
        >
          {headline}
        </div>
      )}

      <div
        style={{
          display: "grid",
          gridTemplateColumns: "repeat(4, 1fr)",
          gap: 16,
          width: "100%",
          maxWidth: 1300,
        }}
      >
        {models.map((m, idx) => {
          const spr = spring({
            frame: Math.max(0, frame - idx * 5),
            fps,
            config: { damping: 14, stiffness: 85 },
          });

          return (
            <div
              key={idx}
              style={{
                background: "rgba(30, 41, 59, 0.65)",
                border: `1.5px solid rgba(255, 255, 255, 0.15)`,
                borderRadius: 16,
                padding: "22px 18px",
                display: "flex",
                flexDirection: "column",
                transform: `scale(${spr})`,
                boxShadow: "0 10px 24px rgba(0,0,0,0.4)",
                backdropFilter: "blur(12px)",
              }}
            >
              <div style={{ fontSize: 32, marginBottom: 10 }}>{m.icon}</div>
              <div style={{ fontSize: 20, fontWeight: 700, color: "#FFFFFF", marginBottom: 4 }}>
                {m.name}
              </div>
              <div
                style={{
                  fontSize: 12,
                  fontWeight: 700,
                  color: m.badgeColor,
                  marginBottom: 12,
                  textTransform: "uppercase",
                  letterSpacing: 1,
                }}
              >
                {m.role}
              </div>
              <div style={{ fontSize: 13, color: "rgba(255,255,255,0.72)", lineHeight: 1.45 }}>
                {m.strengths}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};

// ─────────────────────────────────────────────────────────────
// MẪU 7: Tăng vọt chi phí (Exponential Cost Surge & Money Alert)
// ─────────────────────────────────────────────────────────────
export const ExponentialCostSurge: React.FC<{
  accent?: string;
  kicker?: string;
  headline?: string;
}> = ({
  accent = "#EF4444",
  kicker = "CẢNH BÁO CHI PHÍ",
  headline = "Chi phí token nhân lên cấp số nhân nếu không dọn context",
}) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const progress = interpolate(frame, [0, 60], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  const cost = Math.floor(interpolate(progress, [0, 0.3, 0.7, 1], [8, 45, 380, 2450]));

  return (
    <div
      style={{
        position: "relative",
        width: "100%",
        height: "100%",
        display: "flex",
        flexDirection: "column",
        justifyContent: "center",
        alignItems: "center",
        padding: "0 40px",
      }}
    >
      <Particles count={40} />
      {kicker && (
        <div
          style={{
            fontSize: 16,
            fontWeight: 700,
            letterSpacing: 3,
            color: accent,
            textTransform: "uppercase",
            marginBottom: 8,
          }}
        >
          {kicker}
        </div>
      )}
      {headline && (
        <div
          style={{
            fontSize: 28,
            fontWeight: 700,
            color: "#FFFFFF",
            marginBottom: 24,
            textAlign: "center",
          }}
        >
          {headline}
        </div>
      )}

      <div
        style={{
          display: "flex",
          flexDirection: "column",
          alignItems: "center",
          background: "rgba(239, 68, 68, 0.08)",
          border: "2px solid #EF4444",
          borderRadius: 20,
          padding: "36px 60px",
          boxShadow: "0 0 35px rgba(239, 68, 68, 0.35)",
          backdropFilter: "blur(16px)",
        }}
      >
        <div style={{ display: "flex", alignItems: "center", gap: 14 }}>
          <span style={{ fontSize: 44 }}>💸</span>
          <div style={{ fontSize: 64, fontWeight: 900, color: "#EF4444", letterSpacing: -1 }}>
            ${cost.toLocaleString()}
          </div>
          <span style={{ fontSize: 44 }}>📈</span>
        </div>

        <div style={{ fontSize: 16, color: "rgba(255,255,255,0.75)", marginTop: 8 }}>
          Tốc độ đốt token tăng vọt qua từng vòng chat
        </div>

        <div
          style={{
            marginTop: 18,
            padding: "6px 16px",
            borderRadius: 20,
            background: "rgba(239, 68, 68, 0.2)",
            color: "#EF4444",
            fontSize: 13,
            fontWeight: 800,
            letterSpacing: 1.5,
          }}
        >
          ⚠ CONTEXT PHÌNH TO MỖI LƯỢT
        </div>
      </div>
    </div>
  );
};

