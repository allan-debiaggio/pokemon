import pygame

class Button:
    def __init__(self, x, y, width, height, text, font, color, hover_color, action=None):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.font = font
        self.color = color
        self.hover_color = hover_color
        self.action = action
    
    def draw(self, screen):
        mouse_pos = pygame.mouse.get_pos()
        is_hovered = self.rect.collidepoint(mouse_pos)
        color = self.hover_color if is_hovered else self.color
        
        pygame.draw.rect(screen, color, self.rect, border_radius=10)
        
        border_color = (0, 0, 0) 
        pygame.draw.rect(screen, border_color, self.rect, 3, border_radius=10)
        
        text_surf = self.font.render(self.text, True, (0, 0, 0))
        text_rect = text_surf.get_rect(center=self.rect.center)
        screen.blit(text_surf, text_rect)
        
        if is_hovered:
            triangle_color = (0, 0, 0) 
            triangle_points = [
                (self.rect.left + 10, self.rect.centery - 5),
                (self.rect.left + 10, self.rect.centery + 5),
                (self.rect.left + 20, self.rect.centery)
            ]
            pygame.draw.polygon(screen, triangle_color, triangle_points)
    
    def handle_event(self, event):
        sound = pygame.mixer.Sound("assets/sounds/Button.mp3")
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos) and self.action:
                self.action()
                pygame.mixer.Sound.play(sound)

class Menu:
    def __init__(self, screen, switch_to_submenu):
        self.screen = screen
        self.font = pygame.font.Font(None, 40)
        self.background = pygame.image.load("assets/images/menu_background.jpg")
        self.buttons = [
            Button(200, 150, 400, 50, "Start", self.font, (255, 255, 255), (255, 255, 255), self.start_game),
            Button(200, 250, 400, 50, "Pokedex", self.font, (255, 255, 255), (255, 255, 255), self.pokedex),
            Button(200, 350, 400, 50, "Quit", self.font, (255, 255, 255), (255, 255, 255), pygame.quit),
            Button(200, 450, 400, 50, "Go to SubMenu", self.font, (255, 255, 255), (255, 255, 255), switch_to_submenu)  # Test button
        ]
    
    def start_game(self):
        print("Starting game...")
    
    def pokedex(self):
        print("Pokedex...")
    
    def draw(self):
        # Resize background to fit the screen
        background = pygame.transform.scale(self.background, self.screen.get_size())
        self.screen.blit(background, (0, 0))
        for button in self.buttons:
            button.draw(self.screen)
    
    def handle_event(self, event):
        for button in self.buttons:
            button.handle_event(event)

class SubMenu:
    def __init__(self, screen, switch_to_main_menu):
        self.screen = screen
        self.font = pygame.font.Font(None, 40)
        self.background = pygame.image.load("assets/images/submenu_background.jpg")
        self.buttons = [
            Button(200, 200, 400, 50, "Resume", self.font, (255, 255, 255), (255, 255, 255), self.resume_game),
            Button(200, 300, 400, 50, "Main Menu", self.font, (255, 255, 255), (255, 255, 255), switch_to_main_menu)
        ]
    
    def draw(self):
        background = pygame.transform.scale(self.background, self.screen.get_size())
        self.screen.blit(background, (0, 0))
        for button in self.buttons:
            button.draw(self.screen)
    
    def handle_event(self, event):
        for button in self.buttons:
            button.handle_event(event)

    def resume_game(self):
        print("Resuming game...")

def main():
    pygame.init()
    screen = pygame.display.set_mode((800, 600))
    clock = pygame.time.Clock()
    
    def switch_to_submenu():
        nonlocal current_menu, sound
        pygame.mixer.Sound.stop(sound)
        sound = pygame.mixer.Sound("assets/sounds/Mediator_menu.mp3")
        pygame.mixer.Sound.play(sound, -1)
        current_menu = submenu
    
    def switch_to_main_menu():
        nonlocal current_menu, sound
        pygame.mixer.Sound.stop(sound)
        sound = pygame.mixer.Sound("assets/sounds/Main_menu.mp3")
        pygame.mixer.Sound.play(sound, -1)
        current_menu = menu
    
    menu = Menu(screen, switch_to_submenu)
    submenu = SubMenu(screen, switch_to_main_menu)
    current_menu = menu
    sound = pygame.mixer.Sound("assets/sounds/Main_menu.mp3")
    pygame.mixer.Sound.play(sound, -1)
    
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            current_menu.handle_event(event)
        
        current_menu.draw()
        pygame.display.flip()
        clock.tick(30)
    
    pygame.quit()

if __name__ == "__main__":
    main()
