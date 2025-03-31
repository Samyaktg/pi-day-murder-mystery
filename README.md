
# **π Detective: The Irrational Murder** is a murder mystery game that deeply integrates mathematical concepts of π (pi) with AI-generated content. Designed for Pi-Day celebrations, it features unique π-driven mechanics across all gameplay aspects.

## Core π Integrations

### 1. Dynamic Suspect Generation

- **Killer Selection**: Uses π's 4th digit modulo suspect count to choose murderer[^1]
- **Character Traits**:
    - Ages calculated using π digits[^1]
    - Suspiciousness determined by π digit parity[^1]
    - Motive strength scaled with π digits[^1]


### 2. π-Based Puzzle System

```python
def generate_pi_puzzle(difficulty, position):
    """Generates 3 tiers of π-challenges"""
    # Difficulty modulated by π digits
    difficulty_mod = (difficulty + get_pi_digit(position + 20)) % 3
```

- **Puzzle Types**:
    - Basic arithmetic on π digits
    - Trigonometric challenges using π sequences
    - Algebraic patterns from digit subsequences


### 3. Environment Generation

- **Room Clues**: AI-generated hints containing π references[^1]
- **π Checksum**:

```python
def generate_pi_checksum(data):
    return sum(ord(c) * int(str(math.pi)[i+2]) for i, c in enumerate(data[:10]))
```


## AI Integration

### Gemini AI Features

| Feature | Implementation | π Connection |
| :-- | :-- | :-- |
| Room Generation | Dynamic creation via text prompt | Rooms contain π-related artifacts |
| Visual Design | Image generation with mathematical elements | Subtle π symbolism in textures |
| Dialogue System | Context-aware clue generation | Clues reference π properties |

### AI-Powered Game Flow

1. **Case Initialization**:
    - Generates unique murder scenario using π seed
2. **Room Exploration**:
    - Renders AI-generated 3D environments
    - Creates π-based investigation challenges

## Technical Implementation

### Key Modules

```python
import sympy  # π digit calculation
import google.genai  # AI content generation
import pygame  # Interactive interface
```


### Architecture

**Math Core**
`π Digit Engine → Puzzle Generator → Checksum System`

**AI Layer**
`Gemini API → Content Pipeline → Game State Integration`

**UX System**
`PyGame Interface → Dynamic Rendering → Input Handling`

## Gameplay Mechanics

### Investigation Phases

1. **Scene Analysis**
    - Solve π puzzles to examine rooms
    - Collect AI-generated evidence with math patterns
2. **Suspect Interrogation**
    - Question characters with π-influenced profiles
    - Unlock alibis using digit sequence challenges
3. **Accusation System**
    - Final deduction requires π-based probability calculation
    - Ending determined by π-checksum validated game state

## Security \& Validation

- **Save File Protection**: π-based checksum prevents tampering
- **Anti-Cheat**: Dynamic π digit verification for puzzle answers
- **Privacy**: Local processing of π calculations


## UX Features

- **π-Visual Theme**: Golden ratio layouts, circular interfaces
- **Dynamic Text System**: Auto-cleans AI outputs for π consistency
- **Adaptive Difficulty**: Adjusts based on player's π-solving accuracy


## Hackathon Requirements Coverage

| Requirement | Implementation |
| :-- | :-- |
| π Integration | Core gameplay, RNG, UI |
| AI Usage | Content generation, image synthesis |
| Documentation | This technical spec + in-code comments |
| Prototype | Fully playable build with 3+ cases |
| Interactivity | Mouse/Keyboard controls, puzzle inputs |
| Scalability | Modular case format, AI-powered expansion |

## Future Enhancements

1. **Multiplayer π Mysteries**: Collaborative digit sequence solving
2. **Procedural Generation**: Infinite cases using π digit streams
3. **VR Integration**: 3D π-environment exploration
4. **AI Director**: Dynamic difficulty adjusting via π-based metrics

This implementation demonstrates deep technical integration of π constants while maintaining engaging gameplay, satisfying all hackathon requirements through its unique fusion of mathematics and AI-generated storytelling.



