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
        
        # Draw button background
        pygame.draw.rect(screen, color, self.rect, border_radius=10)
        
        # Draw button border
        border_color = (0, 0, 0)  # Black border
        pygame.draw.rect(screen, border_color, self.rect, 3, border_radius=10)
        
        # Draw button text
        text_surf = self.font.render(self.text, True, (0, 0, 0))
        text_rect = text_surf.get_rect(center=self.rect.center)
        screen.blit(text_surf, text_rect)
        
        # Draw triangle if hovered
        if is_hovered:
            triangle_color = (0, 0, 0)  # Black triangle
            triangle_points = [
                (self.rect.left + 10, self.rect.centery - 5),
                (self.rect.left + 10, self.rect.centery + 5),
                (self.rect.left + 20, self.rect.centery)
            ]
            pygame.draw.polygon(screen, triangle_color, triangle_points)
    
    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos) and self.action:
                self.action()

class Menu:
    def __init__(self, screen):
        self.screen = screen
        self.font = pygame.font.Font(None, 40)
        self.background = pygame.image.load("background.jpg")
        self.buttons = [
            Button(150, 100, 200, 50, "Start", self.font, (255, 255, 255), (255, 255, 255), self.start_game),
            Button(150, 200, 200, 50, "Options", self.font, (255, 255, 255), (255, 255, 255), self.show_options),
            Button(150, 300, 200, 50, "Quit", self.font, (255, 255, 255), (255, 255, 255), pygame.quit)
        ]
    
    def start_game(self):
        print("Starting game...")
    
    def show_options(self):
        print("Showing options...")
    
    def draw(self):
        self.screen.blit(self.background, (0, 0))
        for button in self.buttons:
            button.draw(self.screen)
    
    def handle_event(self, event):
        for button in self.buttons:
            button.handle_event(event)

if __name__ == "__main__":
    pygame.init()
    screen = pygame.display.set_mode((500, 500))
    clock = pygame.time.Clock()
    menu = Menu(screen)
    
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            menu.handle_event(event)
        
        menu.draw()
        pygame.display.flip()
        clock.tick(30)
    
    pygame.quit()
