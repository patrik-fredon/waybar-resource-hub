# Enhanced Design System Guide

## pytfredon-hw GUI Design System

### Overview

This document outlines the comprehensive design system implemented for the pytfredon-hw GUI application. The design system follows modern best practices, WCAG 2.2 AA accessibility standards, and is inspired by Carbon Design System principles.

---

## 🎨 Visual Hierarchy & Typography

### Typography Scale

A perfect 1.25 ratio typographic scale ensuring harmonious size relationships:

| Token             | Size | Usage              | Font Weight    | Line Height |
| ----------------- | ---- | ------------------ | -------------- | ----------- |
| `display-01`      | 46px | Large displays     | 300 (Light)    | 1.2         |
| `display-02`      | 37px | Medium displays    | 300 (Light)    | 1.2         |
| `heading-01`      | 30px | Primary headings   | 600 (Semibold) | 1.2         |
| `heading-02`      | 24px | Secondary headings | 600 (Semibold) | 1.2         |
| `heading-03`      | 18px | Tertiary headings  | 600 (Semibold) | 1.2         |
| `heading-04`      | 15px | Small headings     | 600 (Semibold) | 1.2         |
| `body-01`         | 15px | Body text          | 400 (Regular)  | 1.5         |
| `body-02`         | 12px | Small body text    | 400 (Regular)  | 1.5         |
| `body-compact-01` | 15px | UI elements        | 400 (Regular)  | 1.4         |
| `body-compact-02` | 12px | Small UI elements  | 400 (Regular)  | 1.4         |

### Font Weights

- **300 (Light)**: Large display text, values
- **400 (Regular)**: Body text, UI elements
- **600 (Semibold)**: Headings, emphasis
- **700 (Bold)**: Reserved for high emphasis

### Letter Spacing

- **Large text (30px+)**: -0.02em (tighter)
- **Body text**: 0 (default)
- **Small caps/labels**: +0.05em (looser)

---

## 🌈 Color System & Accessibility

### Color Philosophy

All color combinations meet WCAG 2.2 AA standards (4.5:1 contrast minimum) with many exceeding AAA standards (7:1 contrast).

### Background Colors

```
background: #0b1220           // Primary background (deepest)
background-hover: #0f1626     // Hover states
background-active: #13192c    // Active/pressed states
background-selected: #1a2332  // Selected states
background-brand: #2563eb     // Brand background
```

### Layer Colors (Cards & Surfaces)

```
layer-01: #1c2536             // Primary layer/cards
layer-02: #29344b             // Secondary layer (elevated)
layer-03: #364461             // Tertiary layer (highest)
layer-hover: #334155          // Layer hover states
layer-active: #475569         // Layer active states
```

### Text Colors (WCAG Compliant)

```
text-primary: #f8fafc         // 16.0:1 contrast ✨ AAA
text-secondary: #cbd5e1       // 8.2:1 contrast ✨ AAA
text-tertiary: #94a3b8        // 4.7:1 contrast ✅ AA
text-placeholder: #64748b     // 3.2:1 contrast (Large text only)
text-helper: #94a3b8          // 4.7:1 contrast ✅ AA
```

### Interactive Colors

```
interactive-01: #3b82f6       // Primary actions
interactive-02: #6366f1       // Secondary actions
button-primary: #3b82f6       // Primary buttons
button-primary-hover: #2563eb // Button hover states
```

### Semantic Colors

```
support-error: #ef4444        // Error states
support-warning: #f59e0b      // Warning states
support-success: #10b981      // Success states
support-info: #3b82f6         // Information states
```

### Border Colors

```
border-subtle: #3a4766        // Subtle borders, dividers
border-strong: #5b6a8e        // Strong borders, focus rings
border-interactive: #66a3ff   // Interactive elements
```

---

## 📏 Spacing & Layout System

### 8-Point Grid System

All spacing follows an 8-point grid for consistent alignment:

| Token | Value | Usage           |
| ----- | ----- | --------------- |
| `0`   | 0px   | No spacing      |
| `xs`  | 4px   | Minimal spacing |
| `sm`  | 8px   | Small spacing   |
| `md`  | 12px  | Medium spacing  |
| `lg`  | 16px  | Large spacing   |
| `xl`  | 24px  | Extra large     |
| `2xl` | 32px  | 2X large        |
| `3xl` | 48px  | 3X large        |
| `4xl` | 64px  | 4X large        |

### Component-Specific Spacing

```
button-padding-sm: 8px 16px   // Small buttons
button-padding-md: 12px 24px  // Medium buttons
button-padding-lg: 16px 32px  // Large buttons
input-padding: 12px 16px      // Input fields
card-padding: 16px 24px       // Card content
modal-padding: 24px 32px      // Modal content
```

---

## 🔄 Border Radius System

### Consistent Rounded Corners

| Token  | Value  | Usage            |
| ------ | ------ | ---------------- |
| `none` | 0px    | Sharp corners    |
| `xs`   | 2px    | Minimal rounding |
| `sm`   | 4px    | Small elements   |
| `md`   | 8px    | Medium elements  |
| `lg`   | 12px   | Large elements   |
| `xl`   | 16px   | Extra large      |
| `2xl`  | 24px   | Maximum rounding |
| `full` | 9999px | Pills, circles   |

### Component Radius

```
button: 8px       // Button corners
card: 12px        // Card corners
input: 6px        // Input fields
modal: 16px       // Modal windows
tooltip: 4px      // Tooltips
```

---

## 🏗️ Component Standards

### Card Component

Enhanced metric cards with comprehensive states:

#### States

- **Default**: Clean, accessible baseline
- **Hover**: Elevated with subtle transform
- **Focus**: Clear focus ring for keyboard navigation
- **Active**: Pressed state with reduced elevation
- **Selected**: Highlighted with brand color
- **Loading**: Animated skeleton state

#### Features

- ✅ WCAG AA compliant contrast
- ✅ Keyboard navigation support
- ✅ Screen reader accessibility
- ✅ Status indicators (normal/warning/error/info)
- ✅ Enhanced tooltips with delay
- ✅ Loading states with animations
- ✅ Proper ARIA labels and descriptions

### Button Styles

Consistent button hierarchy with proper states:

#### Primary Buttons

```css
background: #3b82f6
color: #ffffff
border-radius: 8px
padding: 12px 24px
```

#### Secondary Buttons

```css
background: transparent
border: 1px solid #3a4766
color: #f8fafc
border-radius: 8px
```

#### Close Button

```css
background: transparent
color: #94a3b8
hover: background #ef4444, color #ffffff
```

---

## 🎭 Elevation System

### Shadow Hierarchy

Consistent depth perception through elevation:

| Level | Usage             | Shadow                         |
| ----- | ----------------- | ------------------------------ |
| `01`  | Subtle lift       | `0 1px 3px rgba(0,0,0,0.25)`   |
| `02`  | Cards, tooltips   | `0 4px 6px rgba(0,0,0,0.25)`   |
| `03`  | Elevated cards    | `0 10px 15px rgba(0,0,0,0.25)` |
| `04`  | Modals, dialogs   | `0 20px 25px rgba(0,0,0,0.25)` |
| `05`  | Floating elements | `0 25px 50px rgba(0,0,0,0.25)` |

### Interactive Shadows

```css
hover: 0 4px 12px rgba(102,163,255,0.15)  // Blue glow on hover
focus: 0 0 0 2px #60a5fa                  // Focus ring
active: 0 1px 2px rgba(0,0,0,0.25)        // Pressed state
```

---

## ⏱️ Animation System

### Timing Functions

Consistent easing for natural motion:

```css
duration-fast: 150ms      // Quick interactions
duration-moderate: 240ms  // Standard transitions
duration-slow: 400ms      // Complex animations

easing-standard: cubic-bezier(0.4, 0.0, 0.2, 1)    // Standard curve
easing-emphasized: cubic-bezier(0.0, 0.0, 0.2, 1)  // Emphasized motion
easing-decelerated: cubic-bezier(0.0, 0.0, 0.2, 1) // Decelerated
easing-accelerated: cubic-bezier(0.4, 0.0, 1, 1)   // Accelerated
```

### Animation Usage

- **Hover effects**: 240ms standard easing
- **Focus states**: 150ms fast easing
- **Layout changes**: 400ms slow easing
- **Loading states**: Continuous smooth loops

---

## ♿ Accessibility Features

### WCAG 2.2 AA Compliance

- ✅ Minimum 4.5:1 contrast for normal text
- ✅ Minimum 3:1 contrast for large text (18pt+)
- ✅ Minimum 3:1 contrast for UI components
- ✅ Color not used as sole indicator of information

### Keyboard Navigation

- ✅ Logical tab order
- ✅ Visible focus indicators
- ✅ Space/Enter activation for interactive elements
- ✅ Escape key for closing modals

### Screen Reader Support

- ✅ Proper ARIA labels and descriptions
- ✅ Semantic HTML structure
- ✅ Status announcements for dynamic content
- ✅ Alternative text for visual elements

### Enhanced Features

- ✅ Delayed tooltips (500ms) to prevent spam
- ✅ Loading state announcements
- ✅ Error state indicators
- ✅ High contrast mode compatibility

---

## 🎯 Implementation Benefits

### Design Consistency

- Unified visual language across all components
- Predictable interaction patterns
- Maintainable design token system

### Performance

- Optimized animations with proper easing
- HiDPI support for crisp visuals
- Efficient rendering with minimal repaints

### Accessibility

- Legal compliance with accessibility standards
- Inclusive design for all users
- Better usability for assistive technologies

### Developer Experience

- Comprehensive token system
- Clear naming conventions
- Self-documenting code structure

---

## 🔄 Usage Examples

### Applying Typography

```python
# Heading
title.setStyleSheet(f"{TYPOGRAPHY['heading-02']} color: {COLORS['text-primary']};")

# Body text
content.setStyleSheet(f"{TYPOGRAPHY['body-01']} color: {COLORS['text-secondary']};")

# Value display
value.setStyleSheet(f"{TYPOGRAPHY['value']} color: {COLORS['text-secondary']};")
```

### Using Colors

```python
# Card background
f"background-color: {COLORS['layer-01']};"

# Interactive button
f"background-color: {COLORS['button-primary']}; color: {COLORS['text-on-color']};"

# Error state
f"color: {COLORS['text-error']}; border-color: {COLORS['support-error']};"
```

### Applying Spacing

```python
# Layout margins
layout.setContentsMargins(SPACING["xl"], SPACING["xl"], SPACING["xl"], SPACING["xl"])

# Element spacing
layout.setSpacing(SPACING["lg"])

# Component padding
f"padding: {SPACING['card-padding']};"
```

---

## 📚 References

### Design Inspiration

- [Carbon Design System](https://carbondesignsystem.com/) - IBM's open-source design system
- [WCAG 2.2 Guidelines](https://www.w3.org/WAI/WCAG22/quickref/) - Accessibility standards
- [Material Design 3](https://m3.material.io/) - Google's design language

### Typography Resources

- [Typographic Scale Calculator](https://type-scale.com/) - 1.25 ratio implementation
- [Modular Scale](https://www.modularscale.com/) - Mathematical harmony in typography

### Color Resources

- [Accessible Colors](https://accessible-colors.com/) - WCAG compliance checker
- [Contrast Ratio](https://contrast-ratio.com/) - Color contrast verification

---

_This design system ensures a consistent, accessible, and beautiful user experience while maintaining flexibility for future enhancements._
