import math
import pygame


# Calculate the degree
def get_degree(x_vel, y_vel, current_degree):
    # Calculate the arrow angle based on its velocity

    needed_degree = int(math.degrees(math.atan2(-y_vel, x_vel)))

    if int(y_vel) == 0 and int(x_vel) == 0:
        pass
    else:
        rotation_speed = 20  # Adjust this value to control the rotation speed

        # Calculate the difference between the current angle and the target angle
        angle_diff = needed_degree - current_degree

        # If the angle difference is greater than 180 degrees, it's shorter to rotate in the other direction
        if angle_diff > 180:
            angle_diff -= 360
        elif angle_diff < -180:
            angle_diff += 360

        # Update the arrow's angle based on the direction of rotation
        if angle_diff > 0:
            current_degree = min(needed_degree, current_degree + rotation_speed)
        else:
            current_degree = max(needed_degree, current_degree - rotation_speed)

    return int(needed_degree), int(current_degree)


# Calculate distance                 
def find_distance(startx, starty, endx, endy, length=50):
    dx = startx - endx
    dy = starty - endy
    dist = math.hypot(dx, dy)
    angle = math.atan2(dy, dx)
    px = endx + math.cos(angle) * length
    py = endy + math.sin(angle) * length

    return dist, dx, dy, angle, px, py


# Calculate distance 2
def distance(x1, y1, x2, y2):
    return math.sqrt((x1 - x2) ** 2 + (y1 - y2) ** 2)


class PHYSICS:
    def mask_collided(self, obj):
        if self.mask and obj.mask:
            return pygame.sprite.collide_mask(self, obj)
        else:
            return False
    
    @staticmethod
    def get_objects(map, rect, scope=200, grid=False):
        objects = []
        for pos, obs in map.items():
            if not obs[1]:
                continue
            if obs[0].colliderect(rect):
                if grid:
                    objects += list(
                        filter(lambda target: abs(target[0].x - rect.x) <= scope + rect.width and abs(
                            target[0].y - rect.y) <= scope + rect.height,
                            obs[1]))
                else:
                    objects += list(
                        filter(lambda target: abs(target.rect.x - rect.x) < scope + rect.width and abs(
                            target.rect.y - rect.y) < scope + rect.height,
                            obs[1]))
        return objects

    def collide(self, destroy=False, depth=0):
        from .functions import playit
        self.stepping_on_platform = False
        collidedy = False
        collidedx = False
        
        if self.knocking_back:
            self.x_vel = self.knocking_back
            self.knocking_back = 0

        x_vel = int(self.x_vel * self.game.dt)
        y_vel = int(self.y_vel * self.game.dt)

        limit = 64
        if y_vel > limit:
            y_vel = limit

        if x_vel > limit:
            x_vel = limit

        if y_vel < -limit:
            y_vel = -limit

        if x_vel < -limit:
            x_vel = -limit

        if self.zone and y_vel > 200:
            self.y_vel = 200

        if self.type == "weapon" and self.name in ['arrow']:
            _, self.degree = get_degree(x_vel, y_vel, self.degree)
        
        scope = 200
        prev = self.rect.x
        
        self.hit_wall = False
        teleport_x = True
        self.rect.x += x_vel
        
        objects = self.get_objects(self.game.map, self.rect, scope) + self.game.platforms

        for block in objects:
            collidedx = False
            if self.name in ['arrow', 'bomb'] and self.mask and block.mask:
                collide_mask = pygame.sprite.collide_mask(self, block)
            else:
                collide_mask = None

            if self.name in ['arrow', 'bomb']:
                if not collide_mask:
                    continue

            if self.name == 'arrow' and self.type == 'weapon':
                self.stick()
                collidedx = True
                continue

            elif self.rect.colliderect(block.rect):
                collidedx = True
                 
            if collidedx:
                teleport_x = False
                
                if block.type == "moving_platform":
                    if self.nature == "entity" or self.name in ['arrow', 'bomb']:
                        if self.rect.x > block.rect.x:
                            if block.direction[0] == -1:
                                self.x_vel = int((block.speed * block.direction[0]))
                            else:
                                self.x_vel = int((block.speed * -block.direction[0]))
                        else:
                            if block.direction[0] == -1:
                                self.x_vel = int((block.speed * -block.direction[0]))
                            else:
                                self.x_vel = int((block.speed * block.direction[0]))
                        self.stepping_on_platform = True
                            
                if self.x_vel > 0:
                    self.x_vel = 0
                    self.rect.right = block.rect.left
                    self.hit_wall = True
                
                elif self.x_vel < 0:
                    self.x_vel = 0
                    self.rect.left = block.rect.right
                    self.hit_wall = True

        self.rect.y += y_vel
        self.on_ground = False
        for block in objects:
            collidedy = False
            if self.name in ['arrow', 'bomb'] and self.mask and block.mask:
                collide_mask = pygame.sprite.collide_mask(self, block)
            else:
                collide_mask = None
            
            if self.name in ['arrow', 'bomb']:
                if not collide_mask:
                    continue

            if self.name == 'arrow' and self.type == 'weapon':
                self.stick()
                collidedy = True
                continue

            elif self.rect.colliderect(block.rect):
                collidedy = True

            if collidedy:
                if block.type == "moving_platform":
                        if self.nature == "entity" or self.name in ['arrow', 'bomb']:
                            if block.y_vel == 0:
                                self.x_vel = int((block.speed * block.direction[0]))
                                self.y_vel = int((block.speed * block.direction[1]))
                                self.stepping_on_platform = True

                if self.y_vel > 0:
                    self.rect.bottom = block.rect.top

                    if self.nature == "entity":
                        if self.fall_count > 0.3:
                            playit("land", self)

                        if self.fall_count > 0.7:
                            self.health -= int(self.fall_count * 5)

                        if self.type == "player":
                            self.shake_frames = max(self.shake_frames,
                                                    int(self.fall_count * 2))  # Apply shake for next few frames5
                            self.shake_intensity = max(self.shake_intensity, int(self.fall_count * 5))

                    self.landed()
                    if block.type == "moving_platform":
                        if self.nature == "entity" or self.name in ['arrow', 'bomb']:
                            if block.y_vel == 0:
                                self.x_vel = int((block.speed * block.direction[0]))
                                self.y_vel = int((block.speed * block.direction[1]))
                                self.stepping_on_platform = True

                elif self.y_vel < 0:
                    self.rect.top = block.rect.bottom
                    self.y_vel = 0
                    self.hit_head()

                else:
                    if block.type == "moving_platform":
                        if self.nature == "entity" or self.name in ['arrow', 'bomb']:
                            self.rect.bottom = block.rect.top                    
                            self.landed()

        if self.nature == "entity":
            if self.teleport_x:
                if not teleport_x:
                    if self.rect.x > self.game.maxx:
                        self.rect.x = self.game.maxx - 32
                        
                    elif self.rect.x < self.game.minx:
                        self.rect.x = self.game.minx + 32
            
                else:
                    if self.rect.x > self.game.maxx:
                        self.rect.x = self.game.minx + 32
                    
                    elif self.rect.x < self.game.minx:
                        self.rect.x = self.game.maxx - 32
                        
                self.teleport_x = False
                
        if not self.on_ground and self.y_vel > 0:
            self.fall_count += self.game.dt

        # Update hit wall status
        if not self.on_ground:
            self.in_air_for += self.game.dt
        else:
            self.in_air_for = 0

        # Update hit wall status
        if self.on_ground or round(self.in_air_for, 1) < 0.2:
            self.on_ground_for += self.game.dt
        else:
            self.on_ground_for = 0

        # Update hit wall status
        if self.hit_wall:
            self.hit_wall_for += self.game.dt
            self.dashing = False
        else:
            self.hit_wall_for = 0

    def collision_bounce(self, player, target, backfire=True, x=True, y=True):
        try:
            # Calculate normal vector
            normal_x = target.rect.x - player.rect.x
            normal_y = target.rect.y - player.rect.y
            length = math.sqrt(normal_x ** 2 + normal_y ** 2)

            try:
                normal_x /= length
            except:
                normal_x = 0
            try:
                normal_y /= length
            except:
                normal_y = 0

            # Calculate tangent vector
            tangent_x = -normal_y
            tangent_y = normal_x

            # Project velocities onto tangent and normal vectors
            v1n = player.x_vel * normal_x + player.y_vel * normal_y
            v1t = player.x_vel * tangent_x + player.y_vel * tangent_y
            v2n = target.x_vel * normal_x + target.y_vel * normal_y
            v2t = target.x_vel * tangent_x + target.y_vel * tangent_y

            # Perform collision
            v1n, v2n = v2n, v1n

            # Convert back to Cartesian coordinates
            if backfire:
                if x:
                    player.x_vel = v1n * normal_x + v1t * tangent_x
                if y:
                    player.y_vel = (v1n * normal_y + v1t * tangent_y) / 2.5
            if x:
                target.x_vel = v2n * normal_x + v2t * tangent_x
            if y:
                target.y_vel = (v2n * normal_y + v2t * tangent_y)

        except Exception as e:
            print(e)

    def calculate_direction(self, start_x, start_y, end_x, end_y):
        # Calculate the direction vector
        direction_x = end_x - start_x
        direction_y = end_y - start_y
        # Normalize the direction vector
        magnitude = math.sqrt(direction_x ** 2 + direction_y ** 2)
        if magnitude != 0:
            direction_x /= magnitude
            direction_y /= magnitude
        return direction_x, direction_y

    def rect_collision(self, rect1, rect2):
        """Detects collision between two rectangles."""
        return rect1.colliderect(rect2)

    def pathfinding_decision(self, obstacles):
        """
        Look ahead for obstacles.
        If an obstacle's left edge is within SENSOR_DISTANCE from the NPC's right edge
        and there is any vertical overlap, return "jump".
        """
        for obs in obstacles:
            if ((
                        self.direction == 'right' and self.rect.right <= obs.rect.left <= self.rect.right + self.game.SENSOR_DISTANCE) or (
                        self.direction == 'left' and self.rect.left >= obs.rect.right >= self.rect.left - self.game.SENSOR_DISTANCE)) and (
                    self.rect.bottom > obs.rect.top and self.rect.top < obs.rect.bottom):
                return "jump"
        return "move"

    def check_jump(self, dx, dy, objects=None):
        rect = pygame.Rect(self.rect.x + dx * 2.2, self.rect.y + dy + 70, self.rect.width - 10, self.rect.height)
        for obs in objects:
            if obs.rect.colliderect(rect):
                return "move"
        return 'stop'

    def check_fall(self, dx, dy, objects=None):
        if self.type in ['player', 'enemy']:
            off = 20 if dx > 0 else -20
            off1 = 0 if dx > 0 else -30

            self.avoid_fall_rect = pygame.Rect((self.rect.x + off) + (dx * 2), self.rect.bottom, self.rect.width - 20,
                                               self.rect.height + 100)

            self.jump_rect = pygame.Rect((self.rect.x + self.x_vel * 6.5), (self.rect.y + dy), self.rect.width,
                                         self.rect.height - 10)

            self.jump_rect_1 = pygame.Rect((self.rect.x + off1) + self.x_vel * 6.5, self.rect.y + 70, self.rect.width,
                                           self.rect.height)

            for obs in objects:
                if obs.rect.colliderect(self.avoid_fall_rect):
                    return "move"

            for obs in objects:
                if self.chasing:
                    if obs.rect.colliderect(self.jump_rect_1) and not (obs.rect.colliderect(self.jump_rect)):
                        self.x_vel -= 10
                        return "jump and move"

            else:
                return "stop"

    def move(self, dx, dy, objects=None):
        if self.name == "bomb":
            for i in range(4):
                dx = dx / 4
        else:
            if self.type in ['enemy']:

                decision = self.check_fall(dx, dy, objects)

                if "jump" in decision:
                    if self.jump_count < 2:
                        dy = -12
                        self.jump()

                elif "move" in decision:
                    self.rect.x += int(dx * self.game.dt)

            else:
                self.rect.x += int(dx * self.game.dt)

            self.rect.y += int(dy * self.game.dt)

    def accelerate(self):
        self.x_vel = min(self.x_vel + self.acceleration, self.max_vel)

    def decelerate(self, cap=0):
        if not cap:
            cap = self.speed
        if self.x_vel > 0:
            self.x_vel = max(self.x_vel - self.acceleration, 0)
        elif self.x_vel < 0:
            self.x_vel = min(self.x_vel + self.acceleration, 0)

    def make_hit(self):
        self.hit = True

    def move_left(self, vel):
        self.x_vel = -vel
        if self.direction != "left" and not self.attacking:
            self.direction = "left"
            self.animation_count = 0

    def move_right(self, vel):
        self.x_vel = vel
        if self.direction != "right" and not self.attacking:
            self.direction = "right"
            self.animation_count = 0

    def jump(self):
        self.y_vel = self.current_jump
        # self.animation_count = 0
        self.jump_count += 1
        if self.jump_count == 1:
            self.fall_count = 0
        self.on_ground = False

    def swim_up(self):
        self.y_vel = -self.swim_strength * 0.3
        self.jump_count = 0

    def swim_down(self):
        self.y_vel = max(self.y_vel, self.current_jump)

    def landed(self):
        self.fall_count = 0
        self.y_vel = 0
        self.jump_count = 0
        self.on_ground = True

    def hit_head(self):
        self.fall_count = 0
        self.y_vel *= -1
        self.bumped_head = True

    def decide(self):
        enemies = list(filter(lambda target: target.type == 'enemy', self.target_list))
        players = list(filter(lambda target: target.type == 'player', self.target_list))

        def filter_targets(targets_, same_type=None, same_color=None):
            return list(filter(
                lambda target: (same_type is None or (target.name == self.name) == same_type) and
                               (same_color is None or (target.color == self.color) == same_color),
                targets_
            ))

        kill_choice_parts = self.kill_choice.replace('kill', '').strip().split('and')
        target_list = []

        for part in kill_choice_parts:
            part = part.strip()
            if 'enemies' in part:
                targets = enemies
            elif 'players' in part:
                targets = players
            else:
                continue

            if 'with same color' in part:
                target_list.extend(filter_targets(targets, same_color=True))
            elif 'with different color' in part:
                target_list.extend(filter_targets(targets, same_color=False))
            elif 'my' in part:
                target_list.extend(filter_targets(targets, same_type=True))
            else:
                target_list.extend(targets)

        self.target_list = target_list

    def get_nearest(self, target_list, target_list2, times=1):
        my_target = None
        if self.target:
            if self.target.death or self.target.dead:
                self.has_target = False
                self.target = None
        else:
            self.has_target = False
            self.target = None

        # Filter targets within vertical and horizontal range
        targets = []
        for target in target_list:
            if self.type == target.type:
                if target.nature == 'entity':
                    if self.entity_id == target.entity_id or target.death or target.dead:
                        continue  # Skip self as target

            # Check if the target is within vertical and horizontal range
            if (
                    target.rect.top < self.rect.bottom + self.acquire_down and 
                    target.rect.bottom > self.rect.top - self.acquire_up) and (
                    self.rect.centerx - self.acquire_range < target.rect.centerx < self.rect.centerx + self.acquire_range
                ):
                targets.append(target)

        self.targets_in_range = targets
        self.target_list = targets.copy()

        for friend in self.friends:
            if friend in self.target_list:
                self.target_list.remove(friend)

        if times == 1:
            self.decide()

        # If no targets are found in range
        if not self.target_list:
            self.has_target = False
            self.target = None
            if times == 1 and target_list2 and self.mad:
                self.get_nearest(target_list2, self.target_list, 2)
            return

        # Find the target with the minimum distance using Euclidean distance
        min_distance = 2000

        for target in self.target_list:
            # Calculate Euclidean distance between self and the target
            dist, dx, dy, _, _, _ = find_distance(target.rect.centerx, target.rect.centery, self.rect.centerx,
                                                  self.rect.centery)

            if abs(dist) < min_distance:
                min_distance = dist
                my_target = target

        # Assign the nearest target if one is found
        if my_target and not my_target.dead and not my_target.death:
            # If the current target is dead, switch to the new nearest target
            if self.avenger:
                if not self.target.death or self.target.dead:
                    return
                
            self.has_target = True
            self.target = my_target
        else:
            self.has_target = False
            self.target = None

    def knockback(self, dir_="none", target=None):
        
        if not target:
            target = self.target

        if dir_ not in ['left', 'right']:
            if target.rect.centerx > self.rect.centerx:
                target.knocking_back = self.knockback_power # push right

            elif target.rect.centerx < self.rect.centerx:
                target.knocking_back = -self.knockback_power # push left

            
            # print(self.name, self.knockback_power, " : ", target.title, target.knocking_back)
            return
        
        if dir_ == 'left':
            target.knocking_back = -self.knockback_power
        elif dir_ == 'right':
            target.knocking_back = self.knockback_power

        
