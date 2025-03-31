import pygame
import sympy
import math
import random
import time
from google import genai
import sys
import os
from PIL import Image
from io import BytesIO
from google.genai import types

# API configuration
API_KEY = "AIzaSyCC93mbMLR_mjh0N6yX33LA8Oy9XKoMnGE"  # Replace with your actual Gemini API key

# Initialize Pygame
pygame.init()

# Set up the display
WINDOW_WIDTH = 1024
WINDOW_HEIGHT = 768
screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption("π Detective: The Irrational Murder")

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (128, 128, 128)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
GOLD = (212, 175, 55)
DARK_BLUE = (25, 25, 112)

# Fonts
title_font = pygame.font.Font(None, 48)
main_font = pygame.font.Font(None, 32)
small_font = pygame.font.Font(None, 24)

# Game state
class GameState:
    def __init__(self):
        self.screen = "title"
        self.current_stage = 0
        self.questions_asked = 0
        self.clues_found = []
        self.current_suspect = None
        self.current_text = ""
        self.current_puzzle = None
        self.puzzle_answer = None
        self.correct_answers = 0
        self.scroll_offset = 0
        self.max_scroll = 0
        self.killer_index = None
        self.player_accusation = None
        self.game_history = []
        self.suspects = []
        self.rooms = []  # List of rooms will be generated dynamically
        self.current_room = None
        self.room_images = {}
        


    def reset_game(self):
        """Reset the game state for a new playthrough."""
        self.screen = "title"
        self.current_stage = 0
        self.questions_asked = 0
        self.clues_found = []
        self.current_suspect = None
        self.current_text = ""
        self.current_puzzle = None
        self.puzzle_answer = None
        self.correct_answers = 0
        self.scroll_offset = 0
        self.max_scroll = 0
        self.killer_index = None
        self.player_accusation = None
        self.game_history = []
        self.suspects = []
        
    def initialize_game(self):
        """Initialize the game with case description and suspects."""
        case_description, suspects = get_case_description(self)
        self.current_text = case_description
        
        # Generate suspects based on the case
        self.generate_suspects(suspects)
        
        # Generate rooms based on the case
        self.generate_rooms()
        
    def generate_suspects(self, suspects):
        """Generate suspects with their traits based on provided suspects list."""
        # Use PI to select a killer
        self.killer_index = get_pi_digit(3) % len(suspects)
        
        # Generate character details using PI digits
        self.suspects = []
        for i, (name, role) in enumerate(suspects):
            # Use PI to determine traits
            age = 30 + get_pi_digit(i + 5) + get_pi_digit(i + 6) * 10
            # Ensure age does not exceed 90
            age = min(age, 90)
            guilty_traits = get_pi_digit(i + 7) % 2 == 1
            is_killer = (i == self.killer_index)
            motive_strength = get_pi_digit(i + 10) + 1
            
            self.suspects.append({
                "name": name,
                "role": role,
                "age": age,
                "suspicious": guilty_traits or is_killer,
                "is_killer": is_killer,
                "motive_strength": motive_strength,
                "questioned": False,
                "clues": []
            })

    def generate_rooms(self):
        """Generate rooms dynamically using Gemini."""
        # Use the case description to generate relevant rooms
        prompt = f"""
        Generate a list of 3 unique rooms that would be found in the setting of this murder mystery.
        The rooms should be relevant to the case and the suspects.
        Return the rooms as a simple list, separated by commas.
        Example: Study, Kitchen, Ballroom
        """
        
        # Get the case description
        case_description = self.current_text
        if isinstance(case_description, dict):
            case_description = case_description.get("Case Description", "")
        
        # Generate the rooms using Gemini
        rooms_string = generate_ai_content(prompt)
        self.rooms = [room.strip() for room in rooms_string.split(",")]

    # Add this method to the GameState class
    def explore_room(self, room_name):
        """Explore a room and generate a clue."""
        self.current_room = room_name
        
        # Generate room image if it doesn't exist
        if room_name not in self.room_images:
            self.generate_room_image(room_name)
        
        # Generate a clue based on the room
        clue = self.generate_room_clue(room_name)
        self.clues_found.append(f"In the {room_name}: {clean_text_thoroughly(clue)}")
        
        # Set current text as an object with sections for better display
        self.current_text = {
            "Room Exploration": f"You explored the {clean_text_thoroughly(room_name)}",
            "Clue Found": clean_text_thoroughly(clue),
            "Atmosphere": f"The {room_name} reveals its secrets..."
        }
        
        # Reset current stage to normal game state
        self.current_stage = 0

    # Add this method to the GameState class
    def generate_room_image(self, room_name):
        """Generate an image of the room using Gemini."""
        try:
            # Create a detailed prompt for the image
            prompt = f"""
            Create a realistic 3D rendered image of a {room_name}.
            Details:
            - Include relevant objects and furniture for a {room_name}
            - Add a subtle mathematical element to the scene
            - Well-lit, high-quality rendering
            - Make it look like a scene from a mystery game
            """

            # Initialize Gemini client with API key
            client = genai.Client(api_key=API_KEY)  # Use the API_KEY from top of file
            response = client.models.generate_content(
                model="gemini-2.0-flash-exp-image-generation",
                contents=prompt,
                config=types.GenerateContentConfig(
                    response_modalities=['Text', 'Image']
                )
            )

            # Save the generated image
            for part in response.candidates[0].content.parts:
                if part.inline_data is not None:
                    image = Image.open(BytesIO(part.inline_data.data))
                    image = image.resize((WINDOW_WIDTH // 2 - 40, 300))  # Resize to fit the game
                    
                    # Convert PIL Image to Pygame Surface
                    mode = image.mode
                    size = image.size
                    data = image.tobytes()
                    
                    pygame_image = pygame.image.fromstring(data, size, mode)
                    
                    self.room_images[room_name] = pygame_image
                    return True
            
            return False
        except Exception as e:
            print(f"Error generating image for {room_name}: {e}")
            return False

    # Add this method to the GameState class
    def generate_room_clue(self, room_name):
        """Generate a clue based on the room using Gemini."""
        prompt = f"""
        Generate a short clue that could be found in a {room_name} in a murder mystery.
        The clue should be related to mathematics or π in some way.
        Keep it to one sentence and make it specific and observable.
        """
        return generate_ai_content(prompt)
    
    def make_accusation(self, suspect_index):
        if self.questions_asked < 3:
            return "You should question more suspects before making an accusation."
        
        correct = (suspect_index == self.killer_index)
        if correct:
            ending = f"Brilliant deduction! {self.suspects[suspect_index]['name']} is indeed the killer!"
        else:
            ending = f"Wrong! {self.suspects[suspect_index]['name']} is innocent. The real killer was {self.suspects[self.killer_index]['name']}!"
        
        return ending

# --- π-Based Functions ---
def get_pi_digit(position):
    """Retrieves a digit from Pi at a given position, skipping the decimal."""
    pi_string = str(sympy.pi.evalf(position + 10))  # Increase precision
    digits = ''.join(c for c in pi_string if c.isdigit())
    if position < len(digits):
        return int(digits[position])
    else:
        return 0

def get_pi_sequence(start, length=5):
    """Get a sequence of pi digits starting at position start."""
    pi_string = str(sympy.pi.evalf(start + length + 10))
    digits = ''.join(c for c in pi_string if c.isdigit())
    return digits[start:start+length]

def generate_pi_puzzle(difficulty, position):
    """Generates a π-based puzzle or riddle."""
    puzzles = [
        # Easy puzzles (0-3)
        {
            "question": f"What is digit {position} of π?",
            "answer": str(get_pi_digit(position)),
            "type": "direct"
        },
        {
            "question": f"If you add digits {position} and {position+1} of π, what do you get?",
            "answer": str(get_pi_digit(position) + get_pi_digit(position+1)),
            "type": "addition"
        },
        {
            "question": f"If you multiply digit {position} of π by 3, what do you get?",
            "answer": str(get_pi_digit(position) * 3),
            "type": "multiplication"
        },
        {
            "question": f"What is digit {position} of π minus digit {position+1} of π?",
            "answer": str(abs(get_pi_digit(position) - get_pi_digit(position+1))),
            "type": "subtraction"
        },
        
        # Medium puzzles (4-7)
        {
            "question": f"What is the sum of the first {3 + position % 3} digits of π starting from position {position}?",
            "answer": str(sum(int(d) for d in get_pi_sequence(position, 3 + position % 3))),
            "type": "sequence_sum"
        },
        {
            "question": f"If the next 3 digits of π from position {position} represent an angle in degrees, what is its cosine rounded to 2 decimal places?",
            "answer": str(round(math.cos(math.radians(int(get_pi_sequence(position, 3)))), 2)),
            "type": "trigonometry"
        },
        {
            "question": f"If you treat digits {position} to {position+2} of π as a 3-digit number, is it divisible by 7?",
            "answer": "yes" if int(get_pi_sequence(position, 3)) % 7 == 0 else "no",
            "type": "divisibility"
        },
        {
            "question": f"If you arrange the next 4 digits of π starting from position {position} in ascending order, what do you get?",
            "answer": ''.join(sorted(get_pi_sequence(position, 4))),
            "type": "sorting"
        },
        
        # Hard puzzles (8-10)
        {
            "question": f"What is the median of the 5 digits of π starting from position {position}?",
            "answer": str(sorted([int(d) for d in get_pi_sequence(position, 5)])[2]),
            "type": "statistics"
        },
        {
            "question": f"If you create an equation where x equals digit {position} of π and y equals digit {position+1} of π, what is the value of x² + y² - |x-y|?",
            "answer": str(get_pi_digit(position)**2 + get_pi_digit(position+1)**2 - abs(get_pi_digit(position) - get_pi_digit(position+1))),
            "type": "equation"
        },
        {
            "question": f"The sequence of digits in π from position {position} to {position+4} forms a pattern. What is the next number?",
            "answer": str((2 * int(get_pi_sequence(position, 4)[-1]) - int(get_pi_sequence(position, 4)[-2])) % 10),
            "type": "pattern"
        }
    ]
    
    # Use pi to select appropriate difficulty puzzles
    difficulty_mod = (difficulty + get_pi_digit(position + 20)) % 3
    if difficulty_mod == 0:  # Easy
        return puzzles[position % 4]
    elif difficulty_mod == 1:  # Medium
        return puzzles[4 + (position % 4)]
    else:  # Hard
        return puzzles[8 + (position % 3)]

def generate_pi_checksum(data):
    """Generate a simple π-based checksum for save files."""
    return sum(ord(c) * int(str(math.pi)[i+2]) for i, c in enumerate(data[:10]))
def clean_text_thoroughly(text):
    """
    Thoroughly clean text of any special characters, markdown formatting, and non-ASCII characters
    that could cause rendering issues in pygame.
    """
    if not text:
        return ""
        
    # First replace common markdown/formatting patterns
    cleaned = text.replace('**', '').replace('*', '').replace('`', '').replace('"', '').replace('"', '"').replace('"', '"')
    
    # Replace bullet points and other special characters
    cleaned = cleaned.replace('•', '-').replace('…', '...').replace('—', '-').replace('–', '-')
    
    # Replace any unicode quotes or apostrophes with simple versions
    cleaned = cleaned.replace(''', "'").replace(''', "'").replace('′', "'").replace('′', "'")
    
    # Replace other common problematic characters
    cleaned = cleaned.replace('▪', '-').replace('■', '#').replace('□', '#').replace('▫', '-')
    cleaned = cleaned.replace('◆', '*').replace('●', '*').replace('○', 'o').replace('◯', 'o')
    cleaned = cleaned.replace('✓', 'v').replace('✔', 'v').replace('✗', 'x').replace('✘', 'x')
    cleaned = cleaned.replace('\u2022', '-')  # Bullet point
    cleaned = cleaned.replace('\u2013', '-')  # En dash
    cleaned = cleaned.replace('\u2014', '--')  # Em dash
    cleaned = cleaned.replace('\u2018', "'")   # Left single quote
    cleaned = cleaned.replace('\u2019', "'")   # Right single quote
    cleaned = cleaned.replace('\u201C', '"')   # Left double quote
    cleaned = cleaned.replace('\u201D', '"')   # Right double quote
    cleaned = cleaned.replace('\u25A0', '#')   # Black square
    cleaned = cleaned.replace('\u25A1', '#')   # White square
    cleaned = cleaned.replace('\u25CF', '*')   # Black circle
    
    # Filter out any remaining non-ASCII characters (this is the critical part)
    cleaned = ''.join(c if ord(c) < 128 else ' ' for c in cleaned)
    
    # Remove excessive whitespace - collapse multiple spaces into one
    cleaned = ' '.join(cleaned.split())
    
    return cleaned.strip()

def wrap_text(text, font, max_width):
    """Wraps text to fit within a given width."""
    words = text.split(' ')
    lines = []
    current_line = []

    for word in words:
        current_line.append(word)
        if font.size(' '.join(current_line))[0] > max_width:
            current_line.pop()
            lines.append(' '.join(current_line))
            current_line = [word]

    lines.append(' '.join(current_line))
    return lines

# UI Classes
class Button:
    def __init__(self, x, y, width, height, text, action=None, is_pi_choice=False, radius=0):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.action = action
        self.color = RED
        self.is_hovered = False
        self.is_pi_choice = is_pi_choice
        self.radius = radius  # For rounded corners
        self.hover_scale = 1.0
        self.target_scale = 1.0
        
    def update(self):
        # Smooth scale animation
        self.hover_scale += (self.target_scale - self.hover_scale) * 0.2
        
    def draw(self, surface):
        # Scale button based on hover
        scaled_rect = self.rect.copy()
        scaled_rect.width *= self.hover_scale
        scaled_rect.height *= self.hover_scale
        scaled_rect.center = self.rect.center
        
        if self.radius > 0:
            pygame.draw.rect(surface, self.color, scaled_rect, border_radius=self.radius)
            if self.is_hovered:
                pygame.draw.rect(surface, GOLD, scaled_rect, 2, border_radius=self.radius)
        
        # Draw text with shadow
        text_surface = main_font.render(self.text, True, BLACK)
        text_rect = text_surface.get_rect(center=scaled_rect.center)
        shadow_rect = text_rect.move(2, 2)
        shadow_surface = main_font.render(self.text, True, (0, 0, 0, 128))
        surface.blit(shadow_surface, shadow_rect)
        surface.blit(text_surface, text_rect)
        
        if self.is_pi_choice:
            # Mark π-influenced buttons with a small pi symbol
            pi_symbol = small_font.render("π", True, RED)
            pi_rect = pi_symbol.get_rect(topright=(self.rect.right - 5, self.rect.top + 5))
            surface.blit(pi_symbol, pi_rect)

    def handle_event(self, event):
        if event.type == pygame.MOUSEMOTION:
            self.is_hovered = self.rect.collidepoint(event.pos)
            self.color = WHITE if self.is_hovered else GRAY
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if self.is_hovered:
                if self.action:
                    return self.action
                return self.text
        return None

class InputBox:
    def __init__(self, x, y, width, height, text=''):
        self.rect = pygame.Rect(x, y, width, height)
        self.color = BLUE  # Start with blue to indicate active
        self.text = text
        self.active = True  # Start active by default
        self.cursor_visible = True
        self.cursor_timer = 0

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            self.active = self.rect.collidepoint(event.pos)
            self.color = BLUE if self.active else GRAY
        elif event.type == pygame.KEYDOWN:
            if self.active:
                if event.key == pygame.K_RETURN:
                    result = self.text
                    self.text = ''  # Clear text after submitting
                    return result
                elif event.key == pygame.K_BACKSPACE:
                    self.text = self.text[:-1]
                else:
                    self.text += event.unicode
                # Reset cursor blink on key press
                self.cursor_visible = True
                self.cursor_timer = 0
        return None

    def update(self):
        # Blinking cursor logic
        self.cursor_timer += 1
        if self.cursor_timer > 30:  # Toggle every 30 frames (about 0.5 seconds)
            self.cursor_visible = not self.cursor_visible
            self.cursor_timer = 0

    def draw(self, surface):
        # Draw textbox background
        pygame.draw.rect(surface, DARK_BLUE, self.rect, border_radius=5)
        pygame.draw.rect(surface, self.color, self.rect, 2, border_radius=5)
        
        # Draw text
        text_surface = main_font.render(self.text, True, WHITE)
        surface.blit(text_surface, (self.rect.x + 5, self.rect.y + (self.rect.height - text_surface.get_height())//2))
        
        # Draw cursor if active
        if self.active and self.cursor_visible:
            cursor_x = self.rect.x + 5 + text_surface.get_width()
            cursor_y1 = self.rect.y + 5
            cursor_y2 = self.rect.y + self.rect.height - 5
            pygame.draw.line(surface, WHITE, (cursor_x, cursor_y1), (cursor_x, cursor_y2), 2)

class RadialMenu:
    def __init__(self, center_x, center_y, radius, choices):
        self.center_x = center_x
        self.center_y = center_y
        self.radius = radius
        self.buttons = []
        
        # Create buttons in a circular pattern
        num_choices = len(choices)
        for i, choice in enumerate(choices):
            # Filter the choice to remove special characters
            clean_choice = choice.replace('**', '').replace('"', '').strip()
            
            angle = (2 * math.pi * i / num_choices) - (math.pi / 2)
            # Adjust button width based on name length to ensure it fits
            name_width = main_font.size(clean_choice)[0]
            button_width = max(250, name_width + 40)  # Ensure minimum width but expand for longer names
            
            # Adjust position to account for variable width
            x = center_x + radius * math.cos(angle) - button_width//2
            y = center_y + radius * math.sin(angle) - 25
            
            button = Button(x, y, button_width, 40, clean_choice, radius=15)
            self.buttons.append(button)
    
    def draw(self, surface):
        # Draw semi-transparent background
        overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))
        overlay.fill((0, 0, 40))  # Dark blue background
        overlay.set_alpha(200)
        surface.blit(overlay, (0, 0))
        
        # Draw connecting lines
        for button in self.buttons:
            pygame.draw.line(
                surface,
                GOLD,
                             (self.center_x, self.center_y),
                button.rect.center,
                2
            )
        
        # Draw central hub
        pygame.draw.circle(surface, GOLD, (self.center_x, self.center_y), 20)
        pygame.draw.circle(surface, DARK_BLUE, (self.center_x, self.center_y), 18)
        
        # Draw buttons
        for button in self.buttons:
            button.draw(surface)
    
    def handle_event(self, event):
        for button in self.buttons:
            result = button.handle_event(event)
            if result:
                return result
        return None
    
class ScrollableTextBox:
    def __init__(self, x, y, width, height, padding=20):
        self.rect = pygame.Rect(x, y, width, height)
        self.padding = padding
        self.content = ""
        self.scroll_offset = 0
        self.max_scroll = 0
        self.scroll_speed = 20
        self.bg_color = (10, 10, 30)  # Dark blue background
        self.line_height = 30
        self.fade_effect = True
        self.text_sections = []  # For storing different dialogue sections
        
    
    def set_content(self, text_dict):
        """Accept a dictionary of text sections instead of a single string"""
        if isinstance(text_dict, str):
            self.content = clean_text_thoroughly(text_dict)  # Clean entire string
        else:
            # Format different sections with proper spacing and cleaner presentation
            formatted_text = ""
            for section_title, section_text in text_dict.items():
                # Skip section formatting for "Atmosphere" to avoid box
                if section_title == "Atmosphere":
                    formatted_text += f"\n{clean_text_thoroughly(section_text)}\n\n"
                else:
                    formatted_text += f"\n{clean_text_thoroughly(section_title)}:\n"
                    formatted_text += "─" * (len(section_title) + 1) + "\n"  # Separator line
                    formatted_text += f"{clean_text_thoroughly(section_text)}\n\n"
            self.content = formatted_text
        self.calculate_max_scroll()
        
    def calculate_max_scroll(self):
        # Calculate how much scroll is needed based on text height
        wrapped_lines = wrap_text(self.content, main_font, self.rect.width - 2*self.padding)
        total_text_height = len(wrapped_lines) * self.line_height
        visible_height = self.rect.height - 2*self.padding
        self.max_scroll = max(0, total_text_height - visible_height)
        
    def handle_event(self, event):
        if event.type == pygame.MOUSEWHEEL:
            # Scroll up/down with mouse wheel
            self.scroll_offset -= event.y * self.scroll_speed
            # Keep scroll within bounds
            self.scroll_offset = max(0, min(self.scroll_offset, self.max_scroll))
            return True
        return False
        
    def draw(self, surface):
        # Draw background with gradient
        gradient_surface = pygame.Surface((self.rect.width, self.rect.height))
        for i in range(self.rect.height):
            alpha = int(255 * (1 - i/self.rect.height * 0.3))
            pygame.draw.line(gradient_surface, (*self.bg_color, alpha), 
                           (0, i), (self.rect.width, i))
        surface.blit(gradient_surface, self.rect)
        
        # Draw text with sections
        clip_rect = self.rect.inflate(-2*self.padding, -2*self.padding)
        surface.set_clip(clip_rect)
        
        y_offset = self.rect.y + self.padding - self.scroll_offset
        wrapped_lines = wrap_text(self.content, main_font, self.rect.width - 2*self.padding)
        
        for line in wrapped_lines:
            if line.startswith("─"):  # Separator line
                pygame.draw.line(surface, GOLD,
                               (clip_rect.x, y_offset + self.line_height//2),
                               (clip_rect.right, y_offset + self.line_height//2), 1)
            else:
                # Check if this is a section title
                is_title = line.endswith(":")
                font = main_font if not is_title else pygame.font.Font(None, 36)
                color = GOLD if is_title else WHITE
                
                text_surface = font.render(line, True, color)
                if (y_offset + text_surface.get_height() > clip_rect.y and 
                    y_offset < clip_rect.bottom):
                    surface.blit(text_surface, (clip_rect.x, y_offset))
            
            y_offset += self.line_height
            
        surface.set_clip(None)
            
        # Draw scroll indicators if scrollable
        if self.max_scroll > 0:
            if self.scroll_offset > 0:
                # Draw up arrow
                pygame.draw.polygon(surface, WHITE, [
                    (self.rect.right - 20, self.rect.top + 15),
                    (self.rect.right - 30, self.rect.top + 25),
                    (self.rect.right - 10, self.rect.top + 25)
                ])
                
            if self.scroll_offset < self.max_scroll:
                # Draw down arrow
                pygame.draw.polygon(surface, WHITE, [
                    (self.rect.right - 20, self.rect.bottom - 15),
                    (self.rect.right - 30, self.rect.bottom - 25),
                    (self.rect.right - 10, self.rect.bottom - 25)
                ])
                
class Suspect:
    def __init__(self, name, role, age):
        self.name = name
        self.role = role
        self.age = age
        # Sanitize filename: remove special characters and convert spaces to underscores
        safe_filename = ''.join(c for c in name.lower() if c.isalnum() or c.isspace())
        safe_filename = safe_filename.replace(' ', '_')
        self.image_path = f"assets/suspects/{safe_filename}.png"
        
        try:
            # Create suspects directory if it doesn't exist
            os.makedirs("assets/suspects", exist_ok=True)
            
            # Try to load existing image first
            if os.path.exists(self.image_path):
                self.image = pygame.image.load(self.image_path)
            else:
                # If image doesn't exist, try to generate one
                success = self.generate_suspect_image()
                if success:
                    # Load the newly generated image
                    self.image = pygame.image.load(self.image_path)
                else:
                    # If generation fails, create default avatar
                    self.image = self.create_default_avatar()
                    pygame.image.save(self.image, self.image_path)
            
            # Scale the image to correct size
            self.image = pygame.transform.scale(self.image, (150, 150))
            
            # Get description after image is loaded
            self.description = self.get_gemini_description()
            
        except Exception as e:
            print(f"Error handling image for {self.name}: {e}")
            # Ensure we always have a valid image
            self.image = self.create_default_avatar()
            self.description = self.generate_fallback_description()

    def generate_suspect_image(self):
        """Generate an image of the suspect using Gemini."""
        try:
            # Create a detailed prompt for the image
            prompt = f"""
            Create a realistic 3D rendered portrait of {self.name}, a {self.role}.
            Details:
            - Age: {self.age}
            - Professional appearance appropriate for their role
            - Neutral expression with subtle character hints
            - Well-lit, front-facing portrait
            - High-quality, detailed rendering
            - Subtle mathematical elements in their appearance or accessories
            Make it look like a professional character portrait suitable for a mystery game.
            """

            # Initialize Gemini client with API key
            client = genai.Client(api_key=API_KEY)  # Use the API_KEY from top of file
            response = client.models.generate_content(
                model="gemini-2.0-flash-exp-image-generation",
                contents=prompt,
                config=types.GenerateContentConfig(
                    response_modalities=['Text', 'Image']
                )
            )

            # Save the generated image
            for part in response.candidates[0].content.parts:
                if part.inline_data is not None:
                    # Create suspects directory if it doesn't exist
                    os.makedirs("assets/suspects", exist_ok=True)
                    
                    # Save the image
                    image = Image.open(BytesIO(part.inline_data.data))
                    image = image.resize((150, 150))  # Resize to match game requirements
                    image.save(self.image_path)
                    return True
            
            return False
        except Exception as e:
            print(f"Error generating image for {self.name}: {e}")
            # Create a default avatar instead
            default_image = self.create_default_avatar()
            
            # Ensure directory exists
            os.makedirs("assets/suspects", exist_ok=True)
            
            # Save the default avatar as PNG
            pygame.image.save(default_image, self.image_path)
            return False

    def get_random_description(self):
        """Generate a random description based on the suspect's role."""
        appearances = [
            "wearing a meticulously pressed suit",
            "dressed in professional attire",
            "in formal business wear",
            "sporting a sophisticated ensemble",
            "in a carefully coordinated outfit"
        ]
        
        expressions = [
            "maintains unwavering eye contact",
            "shows subtle signs of nervousness",
            "presents a calm demeanor",
            "exhibits careful calculation",
            "displays measured confidence"
        ]
        
        mathematical_quirks = [
            f"frequently checks their watch at π-minute intervals",
            f"arranges items in perfect geometric patterns",
            f"unconsciously traces circular motions",
            f"mutters sequences of numbers under their breath",
            f"draws mathematical symbols while thinking"
        ]
        
        # Use PI to select random elements
        appearance = appearances[get_pi_digit(hash(self.name) % 10) % len(appearances)]
        expression = expressions[get_pi_digit(hash(self.role) % 10) % len(expressions)]
        quirk = mathematical_quirks[get_pi_digit(hash(str(self.age)) % 10) % len(mathematical_quirks)]
        
        return f"{appearance}. {expression}. {quirk}."

    def create_default_avatar(self):
        # Create a surface with a colored circle and text
        surface = pygame.Surface((150, 150), pygame.SRCALPHA)
        pygame.draw.circle(surface, DARK_BLUE, (75, 75), 75)
        text = main_font.render(self.name[0], True, GOLD)
        text_rect = text.get_rect(center=(75, 75))
        surface.blit(text, text_rect)
        return surface
        
    def get_gemini_description(self):
        try:
            # Create a basic description without using image analysis
            prompt = f"""
            Generate a detailed description for {self.name}, a {self.age}-year-old {self.role} who is a suspect in a murder mystery.
            Include:
            1. A professional appearance description (clothing, accessories)
            2. A notable personality trait or mannerism (in a separate line)
            3. A mathematical or π-related quirk in their behavior (in a separate line)
            4. A subtle detail that could be either suspicious or innocent (in a separate line)
            Keep it concise and engaging.
            """
            
            # Get Gemini's text response - Fix the API method call
            client = genai.Client(api_key=API_KEY)
            response = client.models.generate_content(  # Use models.generate_content instead of generate_content
                model="gemini-2.0-flash",
                contents=prompt
            )
            
            # Format the response
            description = f"{self.name}, age {self.age}\n{response.text}"
            return description
        
        except Exception as e:
            print(f"Error getting Gemini description: {e}")
            return self.generate_fallback_description()

    def generate_fallback_description(self):
        # Include role in the description
        return f"{self.name} - {self.role}\nAge: {self.age}\n" \
               f"{self.get_random_description()}"

    def draw(self, surface, x, y):
        # Character description box now occupies the entire left half of the screen
        box_width = WINDOW_WIDTH // 2 - 20  # Half screen width minus margin
        info_rect = pygame.Rect(x, y, box_width, 550)  # Increased height to fill more space
        pygame.draw.rect(surface, DARK_BLUE, info_rect, border_radius=10)
        pygame.draw.rect(surface, GOLD, info_rect, 2, border_radius=10)
        
        # Center the image within the box
        image_x = x + (box_width - self.image.get_width()) // 2
        surface.blit(self.image, (image_x, y + 20))  # Shift image down slightly
        
        # Calculate text area dimensions
        text_margin = 20
        text_area_rect = pygame.Rect(
            info_rect.left + text_margin,
            y + 190,  # Below image
            box_width - 2 * text_margin,
            320  # Increased text area height
        )
        
        y_offset = y + 190
        
        # Draw name with larger font and gold color (clean the name first to remove any ** or special chars)
        clean_name = self.name.replace('*', '').replace('"', '').strip()  # Remove * and "
        name_text = pygame.font.Font(None, 40).render(clean_name, True, GOLD)
        name_rect = name_text.get_rect(centerx=info_rect.centerx, top=y_offset)
        surface.blit(name_text, name_rect)
        y_offset += 40  # Increased spacing after name
        
        # Draw role and age with medium font, wrapping if necessary
        role_age_text = f"{self.role}, age {self.age}"
        wrapped_lines = wrap_text(role_age_text, main_font, box_width - 2 * text_margin)
        
        for line in wrapped_lines:
            role_text = main_font.render(line, True, WHITE)
            role_rect = role_text.get_rect(centerx=info_rect.centerx, top=y_offset)
            surface.blit(role_text, role_rect)
            y_offset += 30
        
        # Draw separator line
        pygame.draw.line(surface, GOLD,
                        (info_rect.left + text_margin, y_offset),
                        (info_rect.right - text_margin, y_offset), 1)
        y_offset += 20
        
        # Get description lines (skip name and role as we've handled them)
        description_lines = self.description.split('\n')[2:]
        
        # Draw each line of the description with proper wrapping - use smaller font
        smaller_font = pygame.font.Font(None, 22)  # Even smaller font for descriptions
        for line in description_lines:
            # Clean the line of any markdown or special characters
            clean_line = clean_text_thoroughly(line)
            # Wrap text to fit within text area width
            wrapped_lines = wrap_text(clean_line, smaller_font, text_area_rect.width)
            for wrapped_line in wrapped_lines:
                if y_offset + 20 <= info_rect.bottom - 10:  # Check if within bounds with padding
                    text = smaller_font.render(wrapped_line, True, WHITE)
                    # Left-align text with proper margin
                    text_rect = text.get_rect(left=text_area_rect.left, top=y_offset)
                    surface.blit(text, text_rect)
                    y_offset += 20  # Smaller line height
            
            # Add small spacing between paragraphs
            y_offset += 5

# --- Game Management ---
def generate_ai_content(prompt, model_name="gemini-2.0-flash"):
    """Generate text using Gemini AI."""
    try:
        client = genai.Client(api_key=API_KEY)
        response = client.models.generate_content(
            model=model_name,
            contents=prompt
        )
        # Thoroughly clean the response
        clean_response = clean_text_thoroughly(response.text)
        return clean_response
    except Exception as e:
        print(f"Error generating AI content: {e}")
        return "Something went wrong with the AI generation. Please try again."

def get_clue_for_suspect(suspect, game_state):
    """Generate a clue about a suspect using PI and Gemini."""
    is_killer = suspect["is_killer"]
    motive_strength = suspect["motive_strength"]
    suspicious = suspect["suspicious"]
    
    # Fix: Use questions_asked as a numeric value instead of current_stage
    pi_mod = get_pi_digit(game_state.questions_asked + 15)
    
    if is_killer and pi_mod > 3:  # Drop subtle hints if killer and PI allows it
        prompt = f"Generate a subtle but revealing clue about {suspect['name']} who is secretly the murderer in a detective story. The clue should hint at their guilt without being obvious."
    elif suspicious and pi_mod > 5:  # Make innocent suspects seem suspicious sometimes based on PI
        prompt = f"Generate a misleading clue about {suspect['name']} in a murder mystery that makes them seem suspicious, even though they are innocent."
    else:  # General clue about character
        prompt = f"Generate a neutral clue about {suspect['name']} in a murder mystery that reveals something about their character or background."
    
    # Add constraint to keep clue short
    prompt += " The clue should be only 1-2 sentences and concrete."
    
    return generate_ai_content(prompt)

def get_case_description(game_state):
    """Generate the initial case description and suspects."""
    # Use PI to influence the scenario
    setting_index = get_pi_digit(1) % 5
    victim_type = get_pi_digit(2) % 3
    murder_weapon_index = get_pi_digit(3) % 4
    time_of_day = ["midnight", "dawn", "dusk", "early morning"][get_pi_digit(4) % 4]
    weather = ["stormy", "misty", "eerily calm", "windswept"][get_pi_digit(5) % 4]
    
    settings = ["mansion", "cruise ship", "remote island", "luxury train", "prestigious university"]
    victims = ["wealthy entrepreneur", "famous scientist", "controversial politician"]
    weapons = ["poison", "antique dagger", "rare toxin", "seemingly accidental fall"]
    
    setting = settings[setting_index]
    victim = victims[victim_type]
    weapon = weapons[murder_weapon_index]
    
    # First, get the suspects from Gemini
    suspects_prompt = f"""
    Generate exactly 6 unique suspects for a mathematical murder mystery set in a {setting}.
    Each suspect should have:
    1. A clear role/occupation related to the {victim} (the victim)
    2. A potential motive
    3. A distinct personality trait
    4. A mathematical quirk or habit

    Format the response as a simple list of 6 names with their roles, like:
    1. [Name] - [Role]
    2. [Name] - [Role]
    etc.

    Keep names and roles concise and memorable.
    """
    
    suspects_response = generate_ai_content(suspects_prompt)
    
    # Parse the suspects response to get just the names and roles
    suspect_lines = [line.strip() for line in suspects_response.split('\n') if line.strip()]
    suspects = []
    for line in suspect_lines:
        if '-' in line:
            # Extract name and role from format "1. Name - Role"
            name_role = line.split('.', 1)[1].strip()
            name, role = name_role.split('-', 1)
            suspects.append((name.strip(), role.strip()))
    
    # Now generate the full case description with these specific suspects
    case_prompt = f"""
    Generate an atmospheric murder mystery case description with these elements:
    - Setting: A {weather} {setting} at {time_of_day}
    - Victim: A {victim}
    - Cause: {weapon}
    - Suspects: {', '.join(f"{name} ({role})" for name, role in suspects)}
    
    The description should:
    1. Create a tense atmosphere
    2. Hint at mathematical patterns or π-related elements in the crime scene
    3. Naturally introduce these specific suspects and their roles
    4. End with "Your mission is to solve this case by questioning suspects and analyzing clues."
    
    Keep it to 3-4 paragraphs and make it engaging.
    """
    
    case_description = generate_ai_content(case_prompt)
    return case_description, suspects

# Add this function near the other helper functions
def get_mathematical_context(game_state):
    """Generate varied mathematical context for dialogues."""
    contexts = [
        f"A clock on the wall showing {round(math.pi, 2)} minutes past the hour",
        f"A bookshelf arranged in a Fibonacci sequence",
        f"Light filtering through hexagonal window panes",
        f"The circular table with {get_pi_digit(game_state.questions_asked)} visible scratches",
        f"Water droplets forming perfect parabolas as they fall"
    ]
    return contexts[game_state.questions_asked % len(contexts)]

# Then modify the get_atmospheric_details function to avoid repetition
def get_atmospheric_details():
    """Generate varied atmospheric details for the scene."""
    # Use a more diverse set of descriptions with no repetition
    time_descriptions = [
        "early morning", "mid-morning", "noon", "afternoon", "evening", "night",
        "golden hour", "first light", "twilight", "witching hour", "dawn", "dusk"
    ]
    
    weather_descriptions = [
        "rain patters against the windows", 
        "thunder rumbles outside",
        "wind howls through the halls",
        "silence hangs heavy in the air",
        "distant footsteps echo down the corridor",
        "a clock ticks rhythmically on the wall",
        "shadows dance across the floor",
        "light filters through dusty curtains",
        "floorboards creak with every movement",
        "voices murmur somewhere far away",
        "the building creaks and settles",
        "a perfectly circular water stain mars the ceiling"
    ]
    
    # Use a combination of PI digits and current question count for variety
    time_idx = (get_pi_digit(7) + get_pi_digit(get_pi_digit(11))) % len(time_descriptions)
    weather_idx = (get_pi_digit(11) + hash(str(time.time())) % 100) % len(weather_descriptions)
    
    return time_descriptions[time_idx], weather_descriptions[weather_idx]


def generate_suspect_response(suspect, question, game_state):
    """Generate a suspect's response to a question."""
    is_killer = suspect["is_killer"]
    pi_influence = get_pi_digit(30) % 10
    
    # Get atmospheric details
    time_of_day, weather = get_atmospheric_details()
    
    context = f"""
    Setting: A tense interrogation during {time_of_day}, with {weather}.
    Suspect's current state: {suspect['name']} {'shows subtle signs of nervousness' if is_killer else 'appears composed but concerned'}
    Mathematical elements present: {get_mathematical_context(game_state)}
    """
    
    if is_killer:
        prompt = f"""
        You are {suspect['name']}, the murderer, being questioned in a mathematical murder mystery.
        Current context: {context}
        
        The detective asks: "{question}"
        
        Respond in character, incorporating:
        1. A subtle mathematical inconsistency in your alibi
        2. Physical mannerisms that hint at deception
        3. An attempt to redirect the conversation
        4. A precise but misleading detail about time or location
        
        Keep the response to 2-3 sentences and maintain the tense atmosphere.
        """
    else:
        prompt = f"""
        You are {suspect['name']}, an innocent suspect in a mathematical murder mystery.
        Current context: {context}
        
        The detective asks: "{question}"
        
        Respond in character, incorporating:
        1. A verifiable mathematical detail about your whereabouts
        2. Natural emotional reactions to being suspected
        3. A genuine attempt to help solve the case
        4. A specific detail that could help prove your innocence
        
        Keep the response to 2-3 sentences and show appropriate concern about the situation.
        """
    
    return generate_ai_content(prompt)

def create_ending(game_state, correct_accusation):
    """Create game ending based on player's accusation."""
    killer = game_state.suspects[game_state.killer_index]["name"]
    accused = game_state.suspects[game_state.player_accusation]["name"]
    
    if correct_accusation:
        prompt = f"""
        Generate a triumphant conclusion for a detective who correctly accused {killer} of murder. 
        Explain how the mathematical clues and π-based puzzles led to this correct conclusion. 
        Keep it to 2-3 paragraphs.
        """
    else:
        prompt = f"""
        Generate a disappointing conclusion for a detective who wrongly accused {accused} when the real killer was {killer}.
        Explain what clues were missed and how the mathematical puzzles should have pointed to the real culprit.
        Keep it to 2-3 paragraphs.
        """
    
    return generate_ai_content(prompt)

class QuestionMenu:
    def __init__(self, suspect):
        self.suspect = suspect
        self.questions = [
            "Where were you when the murder occurred?",
            "What's your connection to the victim?",
            "Can you explain your activities that night?",
            "Did you notice anything unusual?",
            "What do you know about the other suspects?"
        ]
        self.buttons = []
        self.setup_buttons()
        
    def setup_buttons(self):
        y = 400
        for question in self.questions:
            button = Button(100, y, WINDOW_WIDTH - 200, 40, question, radius=15)
            self.buttons.append(button)
            y += 50
            
    def generate_pi_based_response(self, question):
        # Generate response with subtle PI references
        pi_time = round(math.pi * get_pi_digit(hash(question) % 10), 2)
        pi_room = get_pi_digit(hash(self.suspect.name) % 20)
        pi_minutes = int(math.pi * 10) % 60
        
        responses = [
            f"I was in room {pi_room} at exactly {pi_time} o'clock. The clock's hands formed a perfect angle of {round(math.pi * 57.29578, 2)} degrees.",
            f"The victim and I discussed the golden ratio approximately {pi_time} hours before the incident. The conversation lasted precisely {pi_minutes} minutes.",
            f"I heard a strange sound coming from a distance of roughly {round(math.pi * 10, 2)} meters away. The echo repeated {get_pi_digit(5)} times.",
            f"The security footage from camera #{pi_room} should show me walking through the circular garden at {pi_time} PM.",
        ]
        
        return random.choice(responses)

    def draw(self, surface):
        # Draw suspect info at top
        self.suspect.draw(surface, WINDOW_WIDTH//4 - 75, 50)
        
        # Draw question buttons with hover effect
        for button in self.buttons:
            button.draw(surface)

# Initialize game state
game_state = GameState()
buttons = []
text_box = ScrollableTextBox(50, 50, WINDOW_WIDTH - 100, WINDOW_HEIGHT - 250)

# Create initial buttons for title screen
start_button = Button(400,600, 200, 50, "Start Investigation", radius=15)
buttons = [start_button]

# Input box for puzzles
input_box = InputBox(WINDOW_WIDTH//2 - 150, WINDOW_HEIGHT//2, 300, 40)

# Radial menu for suspects
suspect_menu = None

# Main game loop
running = True
while running:
    # Clear screen based on current game screen
    if game_state.screen == "title":
        screen.fill(DARK_BLUE)
        
        # Draw title
        title_text = title_font.render("π Detective: The Irrational Murder", True, GOLD)
        subtitle_text = main_font.render("A Mathematical Murder Mystery", True, WHITE)
        bg = pygame.image.load("BG.png")
        screen.blit(bg,(0,0))
        
        # Draw buttons
        for button in buttons:
            button.draw(screen)

    elif game_state.screen == "game":
        bg = pygame.image.load("BG_Game.png")
        screen.blit(bg,(0,0))
        
        # Draw room image if we have one
        if game_state.current_room and game_state.current_room in game_state.room_images:
            # First draw background
            bg = pygame.image.load("BG_Room.png")
            screen.blit(bg,(0,0))
            
            # Draw room image at the top
            room_image = game_state.room_images[game_state.current_room]
            # Center it horizontally
            image_x = (WINDOW_WIDTH - room_image.get_width()) // 2
            screen.blit(room_image, (image_x, 20))
        
        # Update text box content if needed
        if text_box.content != game_state.current_text:
            text_box.set_content(game_state.current_text)
        
        # Draw the text box below the room image
        text_box_y = 340 if game_state.current_room else 50
        text_box = ScrollableTextBox(50, text_box_y, WINDOW_WIDTH - 100, WINDOW_HEIGHT - text_box_y - 200)
        text_box.set_content(game_state.current_text)
        text_box.draw(screen)
        
        # Update text box content if needed
        if text_box.content != game_state.current_text:
            text_box.set_content(game_state.current_text)
        
        # Draw the text box
        text_box.draw(screen)
        # if game_state.current_room and game_state.current_room in game_state.room_images:
        #     room_image = game_state.room_images[game_state.current_room]
        #     screen.blit(room_image, (10, 10))  # Display the image at the top-left corner
        
        # Draw PI-based progress indicator
        progress = game_state.questions_asked / 22  # 22 total questions
        progress_width = int(WINDOW_WIDTH * progress)
        pygame.draw.rect(screen, BLUE, (0, WINDOW_HEIGHT - 10, progress_width, 10))
        
        # Questions counter with improved styling
        pygame.draw.rect(screen, DARK_BLUE, (WINDOW_WIDTH - 180, 15, 160, 70), border_radius=10)
        pygame.draw.rect(screen, GOLD, (WINDOW_WIDTH - 180, 15, 160, 70), 2, border_radius=10)
        
        question_text = small_font.render(f"Questions: {game_state.questions_asked}/22", True, WHITE)
        screen.blit(question_text, (WINDOW_WIDTH - 165, 25))
        
        # Clues counter
        clues_text = small_font.render(f"Clues: {len(game_state.clues_found)}", True, WHITE)
        screen.blit(clues_text, (WINDOW_WIDTH - 165, 55))
        
        # Draw suspect menu if initialized
        if suspect_menu:
            # Add semi-transparent overlay
            bg = pygame.image.load("BG.png")
            screen.blit(bg,(0,0))
            
            # Draw the menu
            suspect_menu.draw(screen)
        
        
        else:
            # Create regular buttons for main choices
            for button in buttons:
                button.draw(screen)
        
                
    elif game_state.screen == "puzzle":
        screen.fill(DARK_BLUE)
        
        # Draw puzzle text
        puzzle_title = title_font.render("π Puzzle", True, GOLD)
        screen.blit(puzzle_title, (WINDOW_WIDTH//2 - puzzle_title.get_width()//2, 50))
        
        # Draw the puzzle question
        wrapped_lines = wrap_text(game_state.current_puzzle["question"], main_font, WINDOW_WIDTH - 100)
        y_offset = 150
        for line in wrapped_lines:
            text_surface = main_font.render(line, True, WHITE)
            screen.blit(text_surface, (50, y_offset))
            y_offset += 40
        
        # Draw input box
        input_box.draw(screen)
        
        # Draw submit button
        for button in buttons:
            button.draw(screen)
            
    elif game_state.screen == "conclusion":
        screen.fill(BLACK)
        
        # Create dramatic lighting effect
        for i in range(100):
            alpha = 255 - i * 2
            if alpha < 0: alpha = 0
            radius = 300 - i * 2
            s = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
            pygame.draw.circle(s, (0, 0, 40, alpha), (WINDOW_WIDTH//2, WINDOW_HEIGHT//2), radius)
            screen.blit(s, (0, 0))
        
        # Draw ending text with dramatic styling
        if game_state.player_accusation == game_state.killer_index:
            title_text = title_font.render("Case Solved!", True, GOLD)
            # Add dramatic success effect
            glow_surface = pygame.Surface((WINDOW_WIDTH, 100), pygame.SRCALPHA)
            for i in range(20):
                alpha = 150 - i * 7
                if alpha < 0: alpha = 0
                pygame.draw.rect(glow_surface, (212, 175, 55, alpha), (0, i*2, WINDOW_WIDTH, 2))
            screen.blit(glow_surface, (0, 45))
        else:
            title_text = title_font.render("Case Failed!", True, RED)
            # Add dramatic failure effect
            for i in range(3):
                offset = math.sin(time.time() * 5) * 3
                shadow_text = title_font.render("Case Failed!", True, (100, 0, 0))
                screen.blit(shadow_text, (WINDOW_WIDTH//2 - title_text.get_width()//2 + offset, 50 + offset))
            
        screen.blit(title_text, (WINDOW_WIDTH//2 - title_text.get_width()//2, 50))
        
        # Update text box content if needed
        if text_box.content != game_state.current_text:
            text_box.set_content(game_state.current_text)
        
        # Draw the text box
        text_box.draw(screen)
        
        # Draw restart button
        for button in buttons:
            button.draw(screen)
    
    pygame.display.flip()
    
    # Handle events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
            
        # Title screen
        if game_state.screen == "title":
            for button in buttons:
                action = button.handle_event(event)
                if action == "Start Investigation":
                    # Initialize the game with case and suspects
                    game_state.initialize_game()
                    game_state.screen = "game"
                    left_x = WINDOW_WIDTH//4 - 150  # Left column of buttons
                    right_x = WINDOW_WIDTH*3//4 - 150  # Right column of buttons
                    bottom_y = WINDOW_HEIGHT - 120  # Bottom row of buttons
                    top_y = WINDOW_HEIGHT - 180  # Top row of buttons
                    
                    buttons = [
                        Button(left_x, top_y, 300, 50, "Question a Suspect", radius=15),  # Top left
                        Button(right_x, top_y, 300, 50, "Explore a Room", radius=15),    # Top right
                        Button(left_x, bottom_y, 300, 50, "Review Clues", radius=15),     # Bottom left
                        Button(right_x, bottom_y, 300, 50, "Make an Accusation", radius=15)  # Bottom right
                    ]
        
        

        # Main game screen            
        elif game_state.screen == "game":
            if suspect_menu:
                # Handle suspect selection
                suspect_choice = suspect_menu.handle_event(event)
                if suspect_choice:
                    # Find the selected suspect
                    selected_index = None
                    
                    # Handle room exploration (this was missing)
                    if game_state.current_stage == "explore":
                        # Room was selected
                        game_state.explore_room(suspect_choice)
                        suspect_menu = None  # Reset radial menu
                        # Continue game loop without further processing
                        continue
                    
                    # Find suspect index (for other cases)
                    for i, suspect in enumerate(game_state.suspects):
                        if suspect["name"] == suspect_choice:
                            selected_index = i
                            break
                    
                    if selected_index is not None:
                        if game_state.current_stage == "accuse":
                            # Handle accusation
                            game_state.player_accusation = selected_index
                            
                            # Generate dramatic ending based on correctness
                            correct_accusation = (selected_index == game_state.killer_index)
                            killer = game_state.suspects[game_state.killer_index]["name"]
                            accused = game_state.suspects[selected_index]["name"]
                            
                            if correct_accusation:
                                prompt = f"""
                                Generate a dramatic revelation scene where the detective (player) correctly accuses {killer} of being the murderer.
                                Include:
                                1. A tense confrontation
                                2. Reference to mathematical clues that led to this conclusion
                                3. The killer's final confession
                                Keep it to 3-4 paragraphs and make it engaging.
                                """
                            else:
                                prompt = f"""
                                Generate a dramatic scene where the detective (player) wrongly accuses {accused}, but the real killer was {killer}.
                                Include:
                                1. The accused's genuine shock and hurt
                                2. The real killer's subtle triumph
                                3. How the mathematical clues were misinterpreted
                                Keep it to 3-4 paragraphs and make it engaging.
                                """
                            
                            ending = generate_ai_content(prompt)
                            game_state.current_text = ending
                            game_state.screen = "conclusion"
                            
                            # Add a "Play Again" button with dramatic styling
                            buttons = [
                                Button(WINDOW_WIDTH//2 - 100, WINDOW_HEIGHT - 60, 200, 50, "Play Again", radius=15)
                            ]
                            
                        elif game_state.current_stage == "question":
                            # Question the suspect
                            game_state.current_suspect = selected_index
                            suspect_data = game_state.suspects[selected_index]
                            current_suspect = Suspect(suspect_data["name"], suspect_data["role"], suspect_data["age"])
                            
                            # Create question input screen
                            waiting_for_question = True
                            prompt_x = WINDOW_WIDTH // 2 + 10  # Shift to the right
                            prompt_y = 100  # Position below suspect info
                            input_question = InputBox(prompt_x, prompt_y + 40, WINDOW_WIDTH // 2 - 40, 40)  # Position below prompt

                            while waiting_for_question:
                                bg = pygame.image.load("BG_Character.png")
                                screen.blit(bg,(0,0))
                                # Update input box (cursor blinking)
                                input_question.update()
                                
                                # Draw suspect info on the left
                                current_suspect.draw(screen, 10, 20)  # Shift to the left edge
                                
                                # Draw question prompt on the right
                                prompt_text = main_font.render("Type your question:", True, WHITE)
                                screen.blit(prompt_text, (prompt_x, prompt_y))
                                
                                # Draw input box on the right - Draw the SAME instance
                                input_question.draw(screen)
                                
                                pygame.display.flip()
                                
                                # Handle question input - properly handle the input box events
                                for event in pygame.event.get():
                                    if event.type == pygame.QUIT:
                                        pygame.quit()
                                        sys.exit()
                                    
                                    # Handle input box events - Pass the event to the input box
                                    question = input_question.handle_event(event)
                                    
                                    if question:  # When Enter is pressed
                                        waiting_for_question = False
                                        
                                        # Generate π-based mathematical context
                                        pi_digits = [int(d) for d in str(math.pi)[2:20]]
                                        response_seed = sum(ord(c) for c in question) % len(pi_digits)
                                        pi_factor = pi_digits[response_seed]
                                        
                                        # Create mathematical context for the response
                                        math_context = {
                                            "time": f"{round(math.pi * pi_factor % 12, 2)}:{pi_digits[response_seed] * 6:02d}",
                                            "angle": round(math.pi * 57.29578, 2),
                                            "distance": round(math.pi * pi_factor, 2),
                                            "sequence": pi_digits[response_seed:response_seed+4],
                                            "coordinates": (
                                                round(math.cos(math.pi/pi_factor) * 10, 2),
                                                round(math.sin(math.pi/pi_factor) * 10, 2)
                                            )
                                        }
                                        
                                        # Create prompt for Gemini with case context and mathematical element
                                        case_context = game_state.current_text
                                        if isinstance(case_context, dict):
                                            # If it's a dictionary (from a previous question), get the last response
                                            case_context = case_context.get("Response", "")
                                        else:
                                            # If it's the initial case description string, split at "Your mission"
                                            case_context = case_context.split("Your mission")[0]
                                        
                                        if suspect_data["is_killer"]:
                                            prompt = f"""
                                            Context: {case_context}
                                            
                                            You are {suspect_data['name']}, the murderer in this case. You are being questioned by a detective.
                                            The detective asks: "{question}"
                                            
                                            Respond in character, being careful not to reveal your guilt directly. Your response should:
                                            1. Show subtle signs of nervousness or over-calculation
                                            2. Include exactly one of these mathematical elements naturally in your alibi (choose the one that fits most naturally):
                                            - You checked your watch at {math_context['time']}
                                            - You walked at an angle of {math_context['angle']} degrees
                                            - You were approximately {math_context['distance']} meters from an important location
                                            - You noticed a pattern or sequence {math_context['sequence']}
                                            3. Be 2-3 sentences long and sound natural in conversation
                                            4. IMPORTANT: Do not use the exact phrasing "I was X meters from the scene" as it's repetitive
                                            5. IMPORTANT: Avoid mentioning fog pressing against glass or any weather descriptions
                                            
                                            Create a unique response that differs from typical answers.
                                            """
                                        else:
                                            prompt = f"""
                                            Context: {case_context}
                                            
                                            You are {suspect_data['name']}, an innocent suspect in this case. You are being questioned by a detective.
                                            The detective asks: "{question}"
                                            
                                            Respond in character, being truthful but potentially nervous about being suspected. Your response should:
                                            1. Be honest and straightforward
                                            2. Include exactly one of these mathematical elements naturally in your statement (choose the one that fits most naturally):
                                            - You checked your watch at {math_context['time']}
                                            - You walked at an angle of {math_context['angle']} degrees
                                            - You were at a specific position or distance that can be precisely measured
                                            - You noticed a pattern or sequence {math_context['sequence']}
                                            3. Be 2-3 sentences long and sound natural in conversation
                                            4. IMPORTANT: Do not use the exact phrasing "I was X meters from the scene" as it's repetitive
                                            5. IMPORTANT: Avoid mentioning fog pressing against glass or any weather descriptions
                                            
                                            Create a unique response that differs from typical answers.
                                            """
                                        
                                        # Get response from Gemini
                                        response = generate_ai_content(prompt)
                                        
                                        # Generate clue prompt based on the response
                                        clue_prompt = f"""
                                        Generate a short observational clue about {suspect_data['name']}'s behavior
                                        while they answered the question. The clue should involve one of these mathematical elements:
                                        - A spiral pattern with radius {math_context['distance']} units
                                        - {math_context['sequence']} dots arranged in a pattern
                                        - A watch showing {math_context['time']}
                                        - Coordinates {math_context['coordinates']} marked on a map
                                        
                                        If they are {'' if suspect_data['is_killer'] else 'not '}the killer, make the clue subtly
                                        {'suspicious' if suspect_data['is_killer'] else 'innocent'}.
                                        Keep it to one sentence and make it specific and observable.
                                        """
                                        
                                        new_clue = generate_ai_content(clue_prompt)
                                         # Update game state
                                        game_state.questions_asked += 1
                                        game_state.clues_found.append(f"About {suspect_data['name']}: {new_clue}")
                                        time_of_day, current_weather = get_atmospheric_details()
                                        game_state.current_text = {
                                            "Question": question,
                                            "Response": response,
                                            "Observation": new_clue,
                                            "Atmosphere": f"The {current_weather} as {suspect_data['name']} speaks..."
                                        }
                                        text_box.set_content(game_state.current_text)
                                        break
                            
                    # Reset radial menu
                    suspect_menu = None
            else:
                # Handle main game buttons
                for button in buttons:
                    action = button.handle_event(event)
                    if action == "Question a Suspect":
                        # Display suspects in a radial menu with adjusted positioning
                        suspect_choices = [s["name"] for s in game_state.suspects]
                        suspect_menu = RadialMenu(
                            center_x=WINDOW_WIDTH//2,
                            center_y=WINDOW_HEIGHT//2,  # Adjusted center_y
                            radius=250,  # Comfortable radius for button spacing
                            choices=suspect_choices
                        )
                        game_state.current_stage = "question"
                        
                    elif action == "Review Clues":
                        # Show collected clues
                        if game_state.clues_found:
                            clue_text = "Collected Clues:\n\n"
                            for i, clue in enumerate(game_state.clues_found):
                                clue_text += f"{i+1}. {clue}\n\n"
                            game_state.current_text = clue_text
                        else:
                            game_state.current_text = "You haven't collected any clues yet. Question suspects to gather information."
                            
                    elif action == "Make an Accusation":
                        if game_state.questions_asked >= 5:
                            game_state.current_text = "Who do you accuse of the murder? Choose carefully..."
                            suspect_choices = [s["name"] for s in game_state.suspects]
                            suspect_menu = RadialMenu(
                                center_x=WINDOW_WIDTH//2,
                                center_y=WINDOW_HEIGHT//2,  # Adjusted center_y
                                radius=250,
                                choices=suspect_choices
                            )
                            game_state.current_stage = "accuse"
                        else:
                            game_state.current_text = "You don't have enough information to make an accusation yet. Continue investigating."
                    elif action == "Explore a Room":
                        # Display rooms in a radial menu
                        room_choices = game_state.rooms
                        suspect_menu = RadialMenu(
                            center_x=WINDOW_WIDTH//2,
                            center_y=WINDOW_HEIGHT//2,  # Adjusted center_y
                            radius=250,
                            choices=room_choices
                        )
                        game_state.current_stage = "explore"

        if game_state.screen == "game" or game_state.screen == "conclusion":
            text_box.handle_event(event)

        # Puzzle screen
        elif game_state.screen == "puzzle":
            # Handle puzzle input
            answer = input_box.handle_event(event)
            if answer:
                # Check answer on enter key
                if answer.strip().lower() == game_state.puzzle_answer.lower():
                    # Correct answer
                    game_state.correct_answers += 1
                    
                    # Generate a new clue based on success
                    suspect = game_state.suspects[game_state.current_suspect]
                    new_clue = get_clue_for_suspect(suspect, game_state)
                    game_state.clues_found.append(f"About {suspect['name']}: {new_clue}")
                    
                    game_state.current_text = f"Correct! The answer is {game_state.puzzle_answer}.\n\nThrough your mathematical insight, you've uncovered a clue:\n\n{new_clue}"
                else:
                    # Wrong answer
                    game_state.current_text = f"That's not correct. The answer is {game_state.puzzle_answer}.\n\nYour mathematical confusion has caused you to miss important details."
                
                # Return to game screen
                game_state.screen = "game"
                left_x = WINDOW_WIDTH//4 - 150  # Left column of buttons
                right_x = WINDOW_WIDTH*3//4 - 150  # Right column of buttons
                bottom_y = WINDOW_HEIGHT - 120  # Bottom row of buttons
                top_y = WINDOW_HEIGHT - 180  # Top row of buttons

                buttons = [
                    Button(left_x, top_y, 300, 50, "Question a Suspect", radius=15),  # Top left
                    Button(right_x, top_y, 300, 50, "Explore a Room", radius=15),    # Top right
                    Button(left_x, bottom_y, 300, 50, "Review Clues", radius=15),     # Bottom left
                    Button(right_x, bottom_y, 300, 50, "Make an Accusation", radius=15)  # Bottom right
                ]
            
            # Handle submit button
            for button in buttons:
                action = button.handle_event(event)
                if action == "Submit Answer":
                    # Process current answer in input box
                    if input_box.text.strip().lower() == game_state.puzzle_answer.lower():
                        # Correct answer
                        game_state.correct_answers += 1
                        
                        # Generate a new clue based on success
                        suspect = game_state.suspects[game_state.current_suspect]
                        new_clue = get_clue_for_suspect(suspect, game_state)
                        game_state.clues_found.append(f"About {suspect['name']}: {new_clue}")
                        
                        game_state.current_text = f"Correct! The answer is {game_state.puzzle_answer}.\n\nThrough your mathematical insight, you've uncovered a clue:\n\n{new_clue}"
                    else:
                        # Wrong answer
                        game_state.current_text = f"That's not correct. The answer is {game_state.puzzle_answer}.\n\nYour mathematical confusion has caused you to miss important details."
                    
                    # Return to game screen
                    game_state.screen = "game"
                    game_state.scroll_offset = 0  # Reset scroll position
                    buttons = [
                        Button(WINDOW_WIDTH//2 - 150, WINDOW_HEIGHT - 180, 300, 50, "Question a Suspect", radius=15),
                        Button(WINDOW_WIDTH//2 - 150, WINDOW_HEIGHT - 120, 300, 50, "Review Clues", radius=15),
                        Button(WINDOW_WIDTH//2 - 150, WINDOW_HEIGHT - 60, 300, 50, "Make an Accusation", radius=15)
                    ]
        
        # Conclusion screen
        elif game_state.screen == "conclusion":
            # Handle conclusion button
            for button in buttons:
                action = button.handle_event(event)
                if action == "Play Again":
                    # Reset game state for new playthrough
                    game_state.reset_game()
                    game_state.screen = "title"
                    buttons = [start_button]  # Reset to start button
                    text_box.set_content("") # Clear text box content


    # Limit frame rate
    pygame.time.Clock().tick(30)

# Quit the game
pygame.quit()