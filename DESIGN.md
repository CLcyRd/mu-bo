# UI Design System & Color Palette Upgrade

## 1. Overview
This document outlines the upgraded color scheme for the Museum Booking application, focusing on a **Bright & Modern** aesthetic with **Emerald Green (#00C853)** accents. The design prioritizes accessibility (WCAG 2.1) and clear hierarchy.

## 2. Color Palette

### 2.1 Core Colors
| Color Name       | Hex Value | HSLA (Approx)        | Usage Description |
|------------------|-----------|----------------------|-------------------|
| **Emerald Green**| `#00C853` | `hsl(145, 100%, 39%)`| **Accent**: Primary Actions, Selected States, Important Icons. |
| **Success Green**| `#00E676` | `hsl(150, 100%, 45%)`| Success states, softer accents. |
| **Error Red**    | `#D32F2F` | `hsl(4, 66%, 51%)`   | Error states, critical alerts. |

### 2.2 Theme Specifications

#### ☀️ Light Theme (Default - Bright)
*Designed for high brightness (≥80%) and clarity.*

| Token | Hex Value | Contrast (on Bg) | Usage |
|-------|-----------|------------------|-------|
| `--bg-body` | `#F5F7FA` | - | App Background (Light Blue-Grey) |
| `--bg-surface` | `#FFFFFF` | - | Card/Container Backgrounds |
| `--text-primary` | `#1A1A1A` | 15.6:1 (Pass AAA) | Headings, Body Text |
| `--text-secondary`| `#5F6368` | 6.8:1 (Pass AA) | Subtitles, Metadata |
| `--border-color` | `#E0E0E0` | - | Dividers, Borders |
| `--accent-color` | `#00C853` | - | Interactive Elements |
| `--accent-fg` | `#FFFFFF` | **Note:** Use Large Text/Bold or switch to Dark Text (`#000000`) for small text on accent bg. (3.06:1 on White, so only for graphics/large text). **Correction:** On `#00C853` background, use `#000000` text for optimal contrast (10.2:1). |

#### 🌙 Dark Theme
*Designed for low-light environments with high contrast.*

| Token | Hex Value | Contrast (on Bg) | Usage |
|-------|-----------|------------------|-------|
| `--bg-body` | `#121212` | - | App Background |
| `--bg-surface` | `#1E1E1E` | - | Card/Container Backgrounds |
| `--text-primary` | `#E0E0E0` | 13.5:1 (Pass AAA) | Headings, Body Text |
| `--text-secondary`| `#A0A0A0` | 7.2:1 (Pass AA) | Subtitles, Metadata |
| `--border-color` | `#333333` | - | Dividers, Borders |
| `--accent-color` | `#00C853` | 8.3:1 (Pass AA) | Interactive Elements (High visibility on dark) |
| `--accent-fg` | `#000000` | 10.2:1 (Pass AAA) | Text on Accent Background |

## 3. Usage Guidelines (The 15% Rule)
The Emerald Green accent (`#00C853`) must not exceed **15%** of the screen area.
- **DO NOT** use as a full background for the entire page.
- **DO NOT** use for body text (except links/highlights on dark backgrounds).
- **DO** use for:
  - Primary Action Buttons (CTA).
  - Active Navigation Tab Icons.
  - Selected Radio/Checkbox states.
  - Important Status Icons.
  - Progress Bars.

## 4. Typography & Accessibility
- **Primary Text**: Minimum 4.5:1 contrast ratio against background.
- **Large Text**: Minimum 3:1 contrast ratio.
- **Interactive Components**: Graphical objects (icons, button borders) must have 3:1 contrast against adjacent colors. `#00C853` (Emerald) meets this on White (3.06:1) and Dark (8.3:1).

## 5. Component Library Specs

### Buttons
- **Primary**: Background `#00C853`, Text `#000000` (or `#FFFFFF` if large/bold enough, but preferred Black for AAA). Border-radius: `12px`.
- **Secondary**: Transparent Background, Border `1px solid #00C853`, Text `#00C853`.
- **Hover**: Brightness +10% or slight lift.

### Navigation Bar
- **Background**: Surface Color (Blur/Glassmorphism optional).
- **Inactive Item**: Text Secondary.
- **Active Item**: Icon & Label in `#00C853`.

### Cards
- **Background**: Surface Color (`#FFFFFF` or `#1E1E1E`).
- **Shadow**: Soft shadow (`0 4px 12px rgba(0,0,0,0.08)`).
- **Radius**: `16px`.

### Tags/Badges
- **Background**: `rgba(0, 200, 83, 0.1)`.
- **Text**: `#00C853`.
