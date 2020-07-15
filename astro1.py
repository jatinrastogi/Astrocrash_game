import math,random
from superwires import games,color
games.init(screen_width = 640, screen_height = 480, fps=50)
class Explosion(games.Animation):
    sound = games.load_sound('explosion.wav')
    images=['explosion1.bmp','explosion2.bmp','explosion3.bmp','explosion4.bmp','explosion5.bmp','explosion6.bmp','explosion7.bmp','explosion8.bmp','explosion9.bmp']
    def __init__(self,x,y):
        super(Explosion,self).__init__(images=Explosion.images,x=x,y=y,repeat_interval=4,n_repeats=1,is_collideable=False)
        Explosion.sound.play()
class Wrapper(games.Sprite):
    def update(self):
        if self.top > games.screen.height:
            self.bottom = 0
        if self.bottom < 0:
            self.top = games.screen.height
        if self.left > games.screen.width:
            self.right = 0
        if self.right < 0:
            self.left = games.screen.width
    def die(self):
        self.destroy()
class Collider(Wrapper):
    def update(self):
        super(Collider,self).update()
        if self.overlapping_sprites:
            for sprite in self.overlapping_sprites:
                sprite.die()
            self.die()
    def die(self):
        new_explosion = Explosion(x=self.x,y=self.y)
        games.screen.add(new_explosion)
        self.destroy()

class Asteroid(Wrapper):
    SMALL = 1
    MEDIUM = 2
    LARGE = 3
    SPEED = 2
    SPAWN = 2
    POINTS = 30
    total = 0
    images = {SMALL : games.load_image('asteroid_small.bmp'),MEDIUM : games.load_image('asteroid_med.bmp'), LARGE : games.load_image('asteroid_big.bmp')}
    def __init__(self,game,x,y,size):
        super(Asteroid,self).__init__(image=Asteroid.images[size] , x=x , y=y ,dx = random.choice([1,-1]) * Asteroid.SPEED * random.random()/size , dy = random.choice([1,-1]) * Asteroid.SPEED * random.random()/size)
        Asteroid.total += 1
        self.game = game
        self.size = size

    
    def die(self):
        Asteroid.total -= 1
        self.game.score.value += int(Asteroid.POINTS/self.size)
        self.game.score.right = games.screen.width - 10
        if self.size != Asteroid.SMALL:
            for i in range(Asteroid.SPAWN):
                new_asteroid = Asteroid(game = self.game,x=self.x,y=self.y,size=self.size-1)
                games.screen.add(new_asteroid)
        super(Asteroid, self).die()
        if Asteroid.total == 0:
            self.game.advance()
class Ship(Collider):
    image = games.load_image('ship.bmp')
    ROTATION_STEP = 3
    VELOCITY_STEP = 0.03
    MISSILE_DELAY = 25
    VELOCITY_MAX = 3
    sound = games.load_sound('thrust.wav')
    def __init__(self,game,x,y):
        super(Ship,self).__init__(image=Ship.image,x=x,y=y)
        self.missile_wait = 0
        self.game = game

    def update(self):
        super(Ship,self).update()
        if games.keyboard.is_pressed(games.K_LEFT):
            self.angle -= Ship.ROTATION_STEP
        if games.keyboard.is_pressed(games.K_RIGHT):
            self.angle += Ship.ROTATION_STEP
        if games.keyboard.is_pressed(games.K_UP):
            Ship.sound.play()
            angle = self.angle * math.pi / 180
            self.dx += Ship.VELOCITY_STEP * math.sin(angle)
            self.dy += Ship.VELOCITY_STEP * -math.cos(angle)
            self.dx = min(max(self.dx,-Ship.VELOCITY_MAX),Ship.VELOCITY_MAX)
            self.dy = min(max(self.dy,-Ship.VELOCITY_MAX),Ship.VELOCITY_MAX)

        if games.keyboard.is_pressed(games.K_SPACE) and self.missile_wait == 0:
            new_missile = Missile(self.x,self.y,self.angle)
            games.screen.add(new_missile)
            self.missile_wait = Ship.MISSILE_DELAY
        if self.missile_wait > 0:
            self.missile_wait -= 1
    def die(self):
        self.game.end()
        super(Ship, self).die()

class Missile(Collider):
    image = games.load_image('missile.bmp')
    sound = games.load_sound('missile.wav')
    BUFFER = 40
    VELOCITY_FACTOR = 7
    LIFETIME = 40
    def __init__(self,ship_x,ship_y,ship_angle):
        Missile.sound.play()
        angle = ship_angle * math.pi / 180
        buffer_x = Missile.BUFFER * math.sin(angle)
        buffer_y = Missile.BUFFER * -math.cos(angle)
        x = ship_x + buffer_x
        y = ship_y + buffer_y
        dx = Missile.VELOCITY_FACTOR * math.sin(angle)
        dy = Missile.VELOCITY_FACTOR * -math.cos(angle)
        super(Missile,self).__init__(image=Missile.image,x = x,y = y,dx = dx,dy = dy)
        self.lifetime= Missile.LIFETIME
    def update(self):
        super(Missile,self).update()
        self.lifetime -= 1
        if self.lifetime == 0:
            self.destroy()

class Game(object):
    def __init__(self):
        self.level = 0
        self.sound = games.load_sound('level.wav')
        self.score = games.Text(value=0,size=30,color = color.white,top=5,right=games.screen.width-10,is_collideable=False)
        games.screen.add(self.score)
        self.ship = Ship(game=self,x=games.screen.width/2,y=games.screen.height/2)
        games.screen.add(self.ship)
    def play(self):
        games.music.load('theme.mid')
        games.music.play(-1)
        nebula_image = games.load_image('nebula.jpg')
        games.screen.background = nebula_image
        self.advance()
        games.screen.mainloop()
    def advance(self):
        self.level += 1
        BUFFER = 150
        for i in range(self.level):
            x_min = random.randrange(BUFFER)
            y_min = BUFFER - x_min
            x_distance = random.randrange(x_min,games.screen.width - x_min)
            y_distance = random.randrange(y_min,games.screen.height - y_min)
            x = self.ship.x + x_distance
            y = self.ship.y + y_distance
            x %= games.screen.width
            y %= games.screen.height
            new_asteroid = Asteroid(game = self,x=x,y=y,size=Asteroid.LARGE)
            games.screen.add(new_asteroid)
        level_message = games.Message(value='Level' + str(self.level),size=40,color=color.yellow,x=games.screen.width/2,y=games.screen.height/2,lifetime=3*games.screen.fps,is_collideable=False)
        games.screen.add(level_message)
        if self.level>1:
            self.sound.play()
    def end(self):
        end_message = games.Message(value = 'Game Over',size = 90,color=color.red,x=games.screen.width/2,y=games.screen.height/2,lifetime=250,after_death=games.screen.quit,is_collideable=False)
        games.screen.add(end_message)



def main():
    astrocrash = Game()
    astrocrash.play()
main()