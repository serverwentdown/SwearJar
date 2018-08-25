"""
Load a map stored in csv format, as exported by the program 'Tiled.'

Artwork from: http://kenney.nl
Tiled available from: http://www.mapeditor.org/

If Python and Arcade are installed, this example can be run from the command line with:
python -m arcade.examples.sprite_tiled_map
"""

import arcade
import os
import random

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600

# How many pixels to keep as a minimum margin between the character
# and the edge of the screen.
VIEWPORT_MARGIN_X = 256
VIEWPORT_MARGIN_Y = 128

# Physics
MOVEMENT_SPEED = 5
JUMP_SPEED = 14
GRAVITY = 0.5

TAN_FACTOR = 60

# Player configurations
PLAYERS = {
    "isaac": {
        "s": 5, # SPEED
        "a": 0.1, # APPEARING CHANCE
        "c": 0.8, # CURSE CHANCE
        "t": TAN_FACTOR * 0.3 # TEACHER CHANCE
    },
    "rachel": {
        "s": 4,
        "a": 0.2,
        "c": 0.5,
        "t": TAN_FACTOR * 0.3
    },
    "sudharshan": {
        "s": 5,
        "a": 0.2,
        "c": 0.25,
        "t": TAN_FACTOR * 0.2
    },
    "ambrose": {
        "s": 7,
        "a": 0.15,
        "c": 0.5,
        "t": TAN_FACTOR * 0.1
    },
    "yihe": {
        "s": 5,
        "a": 0.2,
        "c": 1.5,
        "t": TAN_FACTOR * 0.4
    }
}

print(PLAYERS)
name = input("choose your player: ")
player = PLAYERS[name]

def p_to_max(p):
    return 60 // p


def get_map(filename):
    """
    This function loads an array based on a map stored as a list of
    numbers separated by commas.
    """
    map_file = open(filename)
    map_array = []
    for line in map_file:
        line = line.strip()
        map_row = line.split(",")
        for index, item in enumerate(map_row):
            map_row[index] = int(item)
        map_array.append(map_row)
    return map_array


class MyGame(arcade.Window):
    """ Main application class. """

    def __init__(self):
        """
        Initializer
        """
        super().__init__(SCREEN_WIDTH, SCREEN_HEIGHT)

        # Set the working directory (where we expect to find files) to the same
        # directory this .py file is in. You can leave this out of your own
        # code, but it is needed to easily run the examples using "python -m"
        # as mentioned at the top of this program.
        file_path = os.path.dirname(os.path.abspath(__file__))
        os.chdir(file_path)

        # Sprite lists
        self.wall_list = None
        self.player_list = None

        # Set up the player
        self.score = 0
        self.player_sprite = None

        self.physics_engine = None
        self.view_left = 0
        self.view_bottom = 0

        self.first_update = True

        self.meep_pop = 0
        self.meep_x = -10000
        self.meep_speed = 0
        self.meep_y = -SCREEN_HEIGHT/2 + 80
        self.meep_swear_show = False

        self.t_pop = 0
        self.t_sprite_change = 0
        self.t_freeze = False
        
        self.intro_show = True

    def setup(self):
        """ Set up the game and initialize the variables. """

        # Sprite lists
        self.player_list = arcade.SpriteList()
        self.wall_list = arcade.SpriteList()

        # Set up the player
        self.player_sprite = arcade.Sprite(f"images/{name}.png", 0.333)

        # Starting position of the player
        self.player_sprite.center_x = 0
        self.player_sprite.center_y = 0
        self.player_list.append(self.player_sprite)

        # TEACHER
        self.t_sprite = arcade.Sprite("images/trf.png", 0.333)
        self.t_sprite.center_x = -10000
        self.t_sprite.center_y = -SCREEN_HEIGHT/2 + 90
        self.wall_list.append(self.t_sprite)

        # Bottom wall
        for left in range(-24000, 24000, 1200//3 - 6):
            wall = arcade.Sprite("images/floor.png", 0.333)
            wall.left = left
            wall.bottom = -SCREEN_HEIGHT + 64
            wall.transparent = True
            wall.alpha = 0.01
            self.wall_list.append(wall)

        self.physics_engine = \
            arcade.PhysicsEnginePlatformer(self.player_sprite,
                                           self.wall_list,
                                           gravity_constant=GRAVITY)

        # Set the background color
        arcade.set_background_color(arcade.color.WHITE)
        # Load the background image. Do this in the setup so we don't keep reloading it all the time.
        # Image from:
        # http://wallpaper-gallery.net/single/free-background-images/free-background-images-22.html
        self.background = arcade.load_texture("images/floor.png")

        # MEEP
        self.meep_texture = arcade.load_texture("images/jiacheng.png")
        self.meep_swear_texture = arcade.load_texture("images/swear.png")
        self.talk_texture = arcade.load_texture("images/talk.png")

        self.intro_texture = arcade.load_texture("images/intro.png")

        # Set the view port boundaries
        # These numbers set where we have 'scrolled' to.
        self.view_left = -SCREEN_WIDTH / 2
        self.view_bottom = -SCREEN_HEIGHT / 2

    def on_draw(self):
        """
        Render the screen.
        """

        # This command has to happen before we start drawing
        arcade.start_render()

        # Draw the background texture
        for left in range(-24000, 24000, 1200//3 - 6):
            arcade.draw_texture_rectangle(left + 200, -SCREEN_HEIGHT + 250, 1200//3, 834//3, self.background)

        if self.meep_pop == 0:
            if random.randint(0, p_to_max(player["a"])) == 0:
                self.meep_pop = random.randint(1, 2)
        elif self.meep_pop == 1: # from left
            self.meep_x = self.view_left - 64
            self.meep_pop = 3
        elif self.meep_pop == 2: # from left
            self.meep_x = self.view_left + SCREEN_WIDTH + 64
            self.meep_pop = 3
        elif self.meep_pop == 3:
            if self.meep_x < self.player_sprite.center_x:
                self.meep_speed = random.uniform(2, 6)
            else:
                self.meep_speed = -random.uniform(2, 6)
            if abs(self.meep_x - self.player_sprite.center_x) < 128:
                self.meep_pop = 5
        elif self.meep_pop == 4:
            self.meep_speed = -self.meep_speed
            self.meep_pop = 5
        elif self.meep_pop == 5:
            if abs(self.meep_x - (self.view_left + SCREEN_WIDTH / 2)) > SCREEN_WIDTH / 2 + 128:
                self.meep_pop = 0
            if random.randint(0, p_to_max(player["c"])) == 0:
                self.score += 1
                self.meep_swear_show = True
            if random.randint(0, p_to_max(player["c"]) // 2) == 0:
                self.meep_swear_show = False

        if self.t_pop == 0:
            if random.randint(0, p_to_max(player["t"])) == 0:
                self.t_pop = random.randint(1, 2)
        elif self.t_pop == 1: # from left
            self.t_sprite.center_x = self.view_left - 64
            self.t_pop = 3
        elif self.t_pop == 2: # from left
            self.t_sprite.center_x = self.view_left + SCREEN_WIDTH + 64
            self.t_pop = 3
        elif self.t_pop == 3:
            if self.t_sprite.center_x < self.player_sprite.center_x:
                self.t_sprite.change_x = random.uniform(3, 8)
            else:
                self.t_sprite.change_x = -random.uniform(3, 8)
            self.t_pop = 4
        elif self.t_pop == 4:
            if arcade.sprite.get_distance_between_sprites(self.t_sprite, self.player_sprite) < 90:
                self.t_sprite.change_x = 0
                self.t_freeze = True
                self.player_sprite.change_x = 0
                self.t_pop = 5
            if arcade.sprite.get_distance_between_sprites(self.t_sprite, self.player_sprite) > SCREEN_WIDTH / 2:
                self.t_pop = 0
        elif self.t_pop == 5:
            if random.randint(0, p_to_max(0.8)) == 0:
                self.t_freeze = False
                self.t_pop = 6
        elif self.t_pop == 6:
            if self.t_sprite.center_x < self.player_sprite.center_x:
                self.t_sprite.change_x = -random.uniform(6, 8)
            else:
                self.t_sprite.change_x = random.uniform(6, 8)
            self.t_pop = 7
        elif self.t_pop == 7:
            if abs(self.t_sprite.center_x - (self.view_left + SCREEN_WIDTH / 2)) > SCREEN_WIDTH / 2:
                self.t_pop = 0

        if self.player_sprite.center_y < -600:
            arcade.draw_text("GAME OVER", self.view_left + SCREEN_WIDTH / 2, self.view_bottom + SCREEN_HEIGHT / 2, arcade.color.BLACK, 24)

        # Draw all the sprites.
        self.player_list.draw()
        self.wall_list.draw()

        self.meep_x = self.meep_x + self.meep_speed
        arcade.draw_texture_rectangle(self.meep_x, self.meep_y, 71, 159, self.meep_texture)
        if self.meep_swear_show:
            arcade.draw_texture_rectangle(self.meep_x + 10, self.meep_y + 120, 82, 55, self.meep_swear_texture)
            
        if self.t_freeze:
            arcade.draw_texture_rectangle(self.player_sprite.center_x + 10, self.player_sprite.center_y + 100, 45, 36, self.talk_texture)
            arcade.draw_texture_rectangle(self.t_sprite.center_x + 10, self.t_sprite.center_y + 100, 45, 36, self.talk_texture)
        
        if self.intro_show:
            arcade.draw_texture_rectangle(SCREEN_WIDTH/2 - 180, SCREEN_HEIGHT/2 - 300, 489//3, 882//3, self.intro_texture)

        # Put the text on the screen.
        # Adjust the text position based on the view port so that we don't
        # scroll the text too.
        #output = f"X: {self.player_sprite.right}\nY: {self.player_sprite.bottom}"
        #arcade.draw_text(output, self.view_left + 10, self.view_bottom + SCREEN_HEIGHT - 50, arcade.color.BLACK, 14)
        
        output = f"SwearJar: ${self.score*50/100}0"
        arcade.draw_text(output, self.view_left + 10, self.view_bottom + SCREEN_HEIGHT - 20, arcade.color.BLACK, 14)

    def on_key_press(self, key, modifiers):
        """
        Called whenever the mouse moves.
        """
        #self.intro_show = False
        if self.t_freeze:
            return
        if key == arcade.key.UP:
            if self.physics_engine.can_jump():
                self.player_sprite.change_y = JUMP_SPEED
        elif key == arcade.key.LEFT:
            self.player_sprite.change_x = -player["s"]
        elif key == arcade.key.RIGHT:
            self.player_sprite.change_x = player["s"]

    def on_key_release(self, key, modifiers):
        """
        Called when the user presses a mouse button.
        """
        if key == arcade.key.LEFT or key == arcade.key.RIGHT:
            self.player_sprite.change_x = 0

    def update(self, delta_time):
        """ Movement and game logic """

        # Call update on all sprites (The sprites don't do much in this
        # example though.)
        self.physics_engine.update()

        # --- Manage Scrolling ---

        # Track if we need to change the view port

        changed = self.first_update
        self.first_update = False

        # Scroll left
        left_bndry = self.view_left + VIEWPORT_MARGIN_X
        if self.player_sprite.left < left_bndry:
            self.view_left -= left_bndry - self.player_sprite.left
            changed = True

        # Scroll right
        right_bndry = self.view_left + SCREEN_WIDTH - VIEWPORT_MARGIN_X
        if self.player_sprite.right > right_bndry:
            self.view_left += self.player_sprite.right - right_bndry
            changed = True

        # Scroll up
        top_bndry = self.view_bottom + SCREEN_HEIGHT - VIEWPORT_MARGIN_Y
        if self.player_sprite.top > top_bndry:
            self.view_bottom += self.player_sprite.top - top_bndry
            changed = True

        # Scroll down
        bottom_bndry = self.view_bottom + VIEWPORT_MARGIN_Y
        if self.player_sprite.bottom < bottom_bndry:
            self.view_bottom -= bottom_bndry - self.player_sprite.bottom
            changed = True

        # If we need to scroll, go ahead and do it.
        if changed:
            arcade.set_viewport(self.view_left,
                                SCREEN_WIDTH + self.view_left,
                                self.view_bottom,
                                SCREEN_HEIGHT + self.view_bottom)


def main():
    window = MyGame()
    window.setup()
    arcade.run()


if __name__ == "__main__":
    main()
