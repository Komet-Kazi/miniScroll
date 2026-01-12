# LED Effect Style Guide

*(Formal Specification v1.0)*

## 1. Core Philosophy

### 1.1 Effect Definition

An effect is a pure animation unit that:

    Maintains its own internal state

    Advances exactly one frame per `step()` call

    Emits a *sparse set of pixel intensities*

    Has no knowledge of hardware, frame timing, or rendering

Effects describe *what should be visible*, not *how it is displayed.*

## 2. Required Interface Contract

All effects *must* subclass `BaseEffect`.

```python
class BaseEffect:
    def step(self) -> list[tuple[int, int, float]]
    def reset(self) -> None
    def is_done(self) -> bool
```

### 2.1 step() (REQUIRED)

Purpose

    Advance the effect by one frame and return visible pixels.

Rules

    One call = one frame

    Must be deterministic given internal state

    Must return a *list* (never `None`)

    Empty list = “nothing visible this frame”

*Return Format:*

```python
(x: int, y: int, brightness: float)
```

    `x`, `y` are *logical matrix coordinates*

    `brightness` is *normalized* (`0.0 ≤ b ≤ 1.0`)

    Values outside range are allowed but will be clamped later

### 2.2 reset() (REQUIRED)

Purpose

    Reinitialize internal state to a clean start.

Rules

    Must be idempotent

    Must not allocate large persistent objects unnecessarily

    Must restore the effect to a usable starting state

    `reset()` is how effects are reused, looped, and layered.

### 2.3 is_done() (OPTIONAL)

Purpose

    Signal whether the effect has completed.

Rules

    Default behavior: return `False`

    Finite effects MUST return `True` eventually

    Continuous effects MUST always return `False`

## 3. Construction Rules (__init__)

### 3.1 Allowed Responsibilities

The constructor may:

    Store configuration parameters

    Validate inputs

    Call `reset()`

```python
def __init__(self, speed=1.0):
    self.speed = speed
    self.reset()
```

### 3.2 Forbidden Responsibilities

🚫 No animation logic
🚫 No matrix queries
🚫 No randomness unless deferred to `reset()`
🚫 No hardware calls

## 4. State Management

### 4.1 State Categories

Each effect should explicitly track:

| *State Type* | *Examples*|
|-|-|
| Spatial  | `x`, `y`, `radius`            |
| Temporal | `step_count`, `time`, `phase` |
| Memory   | `tail`, `history`, `buffer`   |
| Control  | `done`, `direction`           |

### 4.2 Reset Discipline

Every mutable attribute must be initialized in *reset()*.

*Bad*

```python
self.pos += 1  # uninitialized
```

*Good*

```python
def reset(self):
    self.pos = 0
```


## 5. Spatial Rules (Matrix Independence)

⚠️ *Important for upcoming abstraction*

### 5.1 Coordinate System

    `(0, 0)` is the top-left

    `x` increases rightward

    `y` increases downward

Effects *may*:

    Use integer or float internal positions
    Round only at pixel emission time

Effects must not:

    Cache matrix width/height permanently
    Assume fixed dimensions

## 6. Brightness & Visual Energy

### 6.1 Brightness Semantics

Brightness represents *visual intensity*, not logic state.

✔ Allowed:
    Values > 1.0

    Negative values

    Curves (sin, cos, exp)

❌ Forbidden:
    Clamping inside effects

    Hardware brightness scaling

Clamping happens *once*, in the renderer.

## 7. Performance Rules

### 7.1 Sparse Emission

Effects should emit only pixels they affect.

Bad

for x in range(w):
    for y in range(h):
        yield (x, y, 0)


Good

return [(x, y, brightness)]

7.2 Memory Constraints

Trails use collections.deque

No unbounded lists

No per-frame allocation of large grids

## 8. Randomness Policy

### 8.1 Randomness Placement

✔ Randomness allowed in:

reset()

Controlled re-seeding logic

❌ Randomness forbidden in:

step() (unless deterministic per frame)

This guarantees:

Reproducibility

Predictable blending

Debuggability

## 9. Layering & Composition Compatibility

Effects must assume they may be layered.

Therefore:

Do not clear pixels

Do not overwrite brightness logic

Do not assume exclusivity

Layer behavior is controlled externally via BlendMode.

## 10. Effect Categories (Recommended Taxonomy)

Use this mental grouping when designing:

### 10.1 Point Effects

Sparkle

Dot

Comet head

### 10.2 Sweep Effects

Scanner

ZigZag

Radar

### 10.3 Field Effects

Ripples

Noise

Waves

### 10.4 Hybrid Effects

Comet (point + memory)

Pulse waves

Explosions

## 11. Naming Conventions

Classes

CamelCase

Noun or noun-phrase

Examples:

WaveRipple

ScannerSweep

Variables

Descriptive

Directional clarity (dx, dy)

Avoid abbreviations unless standard

## 12. Debugging & Instrumentation

✔ Use ic() sparingly
✔ Never print in step() by default
✔ Debug flags allowed in constructor

## 13. Renderer Assumptions

Effects assume:

Fixed frame duration

One step() call per frame

External timing control

Effects must never:

Sleep

Measure time

Control FPS

## 14. Forward Compatibility: Matrix Abstraction (Preview)

Effects should be written as if:

matrix.width
matrix.height


…will be injected later.

Therefore:

No direct import of scrollphathd in new effects

Dimension queries should be late-bound

We’ll formalize this next.

## 15. Minimal Compliance Checklist

Before calling an effect “done”:

✔ Subclasses BaseEffect
✔ No hardware calls
✔ Clean reset()
✔ Deterministic step()
✔ Sparse pixel output
✔ Layer-safe brightness
