from decimal import Decimal, getcontext, InvalidOperation
from timer_utils import*

#-------Sub classes for Dilation--------#
import pygame
import sys
import os
#--------------------------Inevitable Progression---------------------------#

class OneDDemo:
    def __init__(self, newpage_func=None):
        # Initialize Pygame
        pygame.init()

        # Hide the cursor
        pygame.mouse.set_visible(False)

        # Screen dimensions
        self.width, self.height = 800, 600
        self.screen = pygame.display.set_mode((self.width, self.height))

        # Line start and end points based on a fixed length of 200 units
        line_length = 300
        self.start_pos = ((self.width - line_length) // 2, self.height // 2)
        self.end_pos = (self.start_pos[0] + line_length, self.height // 2)

        # Initial position of the point, starting at the beginning of the line
        self.point_pos = [self.start_pos[0], self.start_pos[1]]

        # Movement unit per key hold
        self.movement_unit = 1

        # Key hold state
        self.left_key_down = False
        self.right_key_down = False

        # Store the function to navigate to a new page
        self.newpage = newpage_func

    def run(self):
        stdin_fd = sys.stdin.fileno()
        stdin_copy = os.dup(stdin_fd)

        print("One D Demo - Use Left/Right arrow keys to move, 'q' to quit")
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_q:
                        running = False  # Quit if 'q' is pressed
                    elif event.key == pygame.K_LEFT:
                        self.left_key_down = True
                    elif event.key == pygame.K_RIGHT:
                        self.right_key_down = True
                elif event.type == pygame.KEYUP:
                    if event.key == pygame.K_LEFT:
                        self.left_key_down = False
                    elif event.key == pygame.K_RIGHT:
                        self.right_key_down = False

            # Move the point if a key is held down
            if self.left_key_down:
                self.point_pos[0] = max(self.start_pos[0], self.point_pos[0] - self.movement_unit)
            if self.right_key_down:
                self.point_pos[0] = min(self.end_pos[0], self.point_pos[0] + self.movement_unit)

            # Fill the screen with a black background
            self.screen.fill((0, 0, 0))

            # Draw the line in white
            pygame.draw.line(self.screen, (255, 255, 255), self.start_pos, self.end_pos, 2)

            # Draw the point in red
            pygame.draw.circle(self.screen, (255, 0, 0), (self.point_pos[0], self.point_pos[1]), 5)

            # Update the display
            pygame.display.flip()

            # Cap the frame rate
            pygame.time.Clock().tick(60)

        # Quit Pygame
        pygame.quit()
        
        # Restore the original standard input
        os.dup2(stdin_copy, stdin_fd)
        os.close(stdin_copy)


   

#--------------------------Spacetime Dilation---------------------------#
    

class TimeDilation:
    def __init__(self, newpage_func):
        self.newpage = newpage_func
        # Set the desired precision to 50 significant digits
        getcontext().prec = 50
        getcontext().Emin = -999999 # Set low to avoid scientific notation

    def show_intro(self, level=0):
        # Base case for the recursive function
        if level == 0:
            reset_activity_timer(300)
            self.newpage()
            intro_text ='''

    Welcome to the Time Dilation Simulator!
            
            Discover the intriguing effects of gravity on time through the eyes of three observers:
                1. You: Observe from a neutral point, where time flows consistently at 1 unit per second.
                2. Observer A: Moves towards gravity, experiencing time more slowly.
                3. Observer B: Moves away from gravity, where time speeds up.
            
            How It Works:
                * Movement "Left": 
                    - Adds gravity for Observer A, slowing their time.
                    - Reduces gravity for Observer B, speeding up their time.
                * Movement "Right":
                    - Consistent flow  of time where all observers are stationary
                
            Your Mission: Watch as Observer A aims for a target. Your actions influence their journey, 
                showcasing how gravity bends the fabric of time.

                Ready to see time warp before your eyes?
            
        Press 'enter' to begin, or type "expand" and press 'enter' to read further!\n'''
            
        elif level == 1:
            reset_activity_timer(300)
            self.newpage()
            intro_text = '''
    The Triangle of Observers:

            Imagine a triangle where each point represents one of the three observers. Initially, 
            all are at the same point—forming a perfect equilateral triangle. You're at the base, 
            Observer A is at the top left, and Observer B at the top right. Initially, all exist 
            in a state free from any relativistic effects of time dilation.

            Movement and Time Dilation:
                * Right Movement (Time at Rest): Selecting a 'right' move keeps the triangle's structure 
                    intact but lets time tick uniformly for all observers. This is a pause, allowing 
                    every observer to experience time at a consistent rate within their frame.
                * Left Movement (Spatial Expansion): Opting for a 'left' move makes the triangle expand. 
                    Observer A heads towards a weaker gravitational field, while Observer B moves towards 
                    a stronger one. This expansion is spatial—each observer drifts 1 unit per second from 
                    your viewpoint, ignoring the dilation initially, but introduces the dilation effects 
                    observed in the simulation (an equilateral triangle that distorts).

            Visualizing the Triangle:
                With each 'left' move, the triangle's expansion visually depicts the varying perceptions 
                of time due to gravity's relativistic impacts:

                * The side leading to Observer A, moving into stronger gravity, elongates slower, mirroring 
                    their stretched time.
                * The side reaching towards Observer B, heading into lesser gravity, lengthens faster, 
                    signifying their quicker passage of time from your perspective.
            
            The Observer's Perspective:
                From your position at the triangle's base, you watch the two vertices separate with each 
                'left' move. This divergence in their temporal experiences is symbolized by the triangle's 
                expansion. It acts as a metaphor for spacetime stretching under gravity's sway, influencing 
                each observer's time flow.
                
        Press 'enter' to begin, or type "expand" and press 'enter' to read further!\n'''
                    

        elif level == 2:
            reset_activity_timer(300)
            self.newpage()
            intro_text = '''
    Understanding Physical Space and Spacetime
        
        In our journey through the relativistic effects of gravity on time, we've visualized the movement 
        of our observers as an expanding equilateral triangle in physical space. We must consider two 
        perspectives on the situation at hand. On where the triangle exists in physical space, and another 
        where the triangle exists in spacetime 'iSpace'.
        
        The Equilateral Triangle in Physical Space:
            * Unchanged Proportions: In physical space, given each frame of reference, each observer would 
                'see' the triangle as equilateral uniformly expanding with each 'left' movement. This 
                represents each observer moving symmetrically away from the starting point, maintaining equal 
                spatial relations with one another. This is true given their frame of observation.
            * Constant Spatial Movement: Despite the gravitational effects, the physical space between the 
                observers expands at a constant rate, perceived as 1 unit per second from your perspective. 
                This uniform expansion symbolizes the physical distance they cover, irrespective of the 
                relativistic time effects.
        
        The Triangle in Spacetime (iSpace): A Unified Perspective
            As the observers expand from one another, they perceive an expanding equilateral triangle 
            respective to their own gravitational context. However, each observer percieving their own clock 
            as 'normal' would visualize the other two observers as having changing rates. This divergence in 
            time perception affects how each observer views the expansion of the triangle.
            
            Spacetime: A Perspective Binding Fabric
                * Composite Frames: Spacetime serves as a canvas that merges these individual perceptions 
                    into a singular, unified frame. This frame draws an equilateral triangle that accomodates 
                    all frames into one, but by doing so, this triangle 'bends' inwards and outwards to 
                    accomodate for each perspective.
                * Percieved Geometry: Within this unified spacetime framework, what appears as an equilateral 
                    triangle in each observer's frame transforms when viewed from the comprehensive spacetime 
                    perspective. The triangle's sides, representing the paths between observers, no longer 
                    conform strictly to equilateral geometry due to the curvature induced by differing time 
                    flows.
                        - Think of it like a strange shape. When you look at it, it looks 'normal', but when 
                            you rotate it, it's completely different than how it originally looked. It's 
                            still the same shape, just differs based on how you look at it!

            Bridging Individual Realities:
                * Relativity of Straight Lines: Ever heard "The shortest distance between two points is not 
                    always a straight line"?, well this is exactly why! Just as a straight line in spacetime 
                    can curve, so too can our equilateral triangle warp, accomodating the realtive nature of 
                    time and space as experienced by each observer.
                * The Illusion of Equilaterality: While each observer perceives an equilateral triangle 
                    expanding within their frame, the incorporation of these perspectives into the singular
                    spacetime grid reveals a more complex shape, illustrating the relativistic interplay
                    between space and time. 

        Press 'enter' to begin, or type "expand" and press 'enter' to read further!\n'''
        
        elif level == 3:
            reset_activity_timer(300)
            self.newpage()
            intro_text = '''
    Spacetime Through the Lens of Complex Numbers

        In mathematics, complex numbers offer a way to extend the real number line by introducing an 
        imaginary component, denoted by 'i'. This concept mirrors the fabric of spacetime, where the "real" 
        part corresponds to our observable dimensions and the "imaginary" part represents the hidden 
        dimensions or effects, like time dilation, that we can't directly perceive.

        Spacetime and Complex Numbers:
        * Real Component: In the context of spacetime, the real component can be likened to the observable 
            spatial dimensions within an observer's frame. This is the part of spacetime that we can 
            directly measure and perceive.
        * Imaginary Component: The imaginary part of spacetime, akin to the imaginary unit 'i' in complex 
            numbers, symbolizes the aspects of spacetime that elude direct perception, such as the 
            curvature induced by gravity. This component accounts for the "bending" of spacetime, allowing 
            for phenomena like time dilation.

        The Scaling Quantity in Spacetime:
            * Defining Curvature: Just as the magnitude of the imaginary part in a complex number defines 
                the extent of deviation from the real axis, the "scaling quantity" in spacetime represents 
                the degree to which time and space are curved due to gravitational effects. This curvature 
                allows spacetime to "stretch" or "compress," accommodating more events or distances within 
                a given segment of the real (observable) part.
            * Storing Values Along the 'Invisible' Line: The imaginary component in complex numbers allows 
                us to represent values and operations that don't fit on the traditional real number line. 
                Similarly, the "imaginary" aspect of spacetime enables us to conceptualize how an observer 
                can traverse or experience more space or time than what appears constrained by the real 
                dimensions, like fitting 20 units of experience within a 5-unit span of observable space.

        Mathematical Insights into Relativity:
            This mathematical analogy sheds light on the intricacies of spacetime and relativity, offering 
            a way to grasp the otherwise abstract concepts of time dilation and spacetime curvature. It 
            highlights how spacetime accommodates the vast range of relativistic phenomena within a coherent 
            framework, much like how complex numbers encompass both real and imaginary components to form a 
            complete picture.
            
            Press 'enter' to begin, or type "expand" and press 'enter' to see the raw code!\n'''
        
        elif level == 4:
            reset_activity_timer(300)
            self.newpage()
            intro_text = '''
    Raw Code of the math in the Program:

                # Update position based on input
                if move == 'l':
                    observer_position -= Decimal('1')
                elif move == 'r':
                    observer_position += Decimal('1')
                elif move == 'e':  # Exit condition
                    break
                else:
                    continue  # If the input is not recognized, continue to the next iteration

                curr_distance = calculate_distance(observer_position, target_position)

                # In the event of moving 'away' from point or 'decelerating'
                # '+1' accounts for the first step rate to avoid division by zero
                observerA_time_dilation_rate = (target_position - observerA_spacetime_traveled) 
                                                / (curr_distance + Decimal('1'))
                #Flip perspective calculations
                observerB_time_contraction_rate = Decimal('1') / observerA_time_dilation_rate

                # Adds the rate to the distance for one unit of movement
                observerA_spacetime_traveled += observerA_time_dilation_rate
                # Flip real distance
                observerB_spacetime_traveled += observerB_time_contraction_rate

                # Final point for flipped perspective
                observerB_extended_target = observerB_spacetime_traveled 
                                            + ((observerB_time_contraction_rate**Decimal('2'))
                * (target_position - observerA_spacetime_traveled))

                your_spacetime_traveled += Decimal('1')  # Increment total distance considering imaginary
        
            Press 'enter' to begin, or type "expand" and press 'enter' to read further into the workings!\n'''

        elif level == 5:
            reset_activity_timer(360)
            self.newpage()
            intro_text = '''
    Further Explanation

        observer_position:
            Role: Represents the current spatial position of the observer in the simulation along 
                a one-dimensional axis.
            Calculation: Incremented or decremented by 1 unit with each 'right' or 'left' input, 
                simulating movement towards or away from the target in spacetime.
            
        target_position:
            Role: Denotes the destination or target point in spacetime that the observer aims 
                to reach.
            Calculation: Set by user input at the start and remains constant, serving as the 
                fixed point towards which the observer moves.
    
        observerA_spacetime_traveled:
            Role: Accumulates the total spacetime distance traveled by Observer A, taking into 
                account the effects of time dilation as they move towards a stronger gravitational field.
            Calculation: Updated with each movement based on observerA_time_dilation_rate, 
                reflecting the slowed progression through spacetime due to gravity.
        
        observerA_time_dilation_rate: *** PRIMARY FORMULA ***
            Role: Determines the rate at which time dilates for Observer A as they move towards or away 
                from the target, simulating the influence of gravity on their passage through spacetime.
            Calculation: (target_position - observerA_spacetime_traveled) / (curr_distance + 1), 
                which adjusts the observer's pace based on their remaining distance to the target and 
                simulates time dilation.
        
        observerB_time_contraction_rate:
            Role: Represents the rate of time contraction for Observer B, moving in the opposite conceptual 
                direction to Observer A and experiencing faster progression through spacetime.
            Calculation: 1 / observerA_time_dilation_rate, the reciprocal of Observer A's time dilation 
                rate, illustrating the inverse relationship between time dilation and contraction.
        
        observerB_spacetime_traveled:
            Role: Tracks the total spacetime distance covered by Observer B, accounting for the effects of 
                time contraction as they move away from stronger gravity.
            Calculation: Incremented by observerB_time_contraction_rate with each 'left' movement, 
                reflecting the accelerated progression through spacetime.
        
        your_spacetime_traveled:
            Role: Measures the spacetime distance you, as the program's user and the third observer, have 
                traversed during the simulation.
            Calculation: Incremented by 1 unit with each input ('left' or 'right'), representing your 
                steady progression through spacetime at a constant rate.
        
        observerB_extended_target:
            Role: For Observer B, this variable signifies the extended target position in spacetime, 
                considering the expanded spacetime they traverse due to time contraction.
            Calculation: observerB_spacetime_traveled + (observerB_time_contraction_rate**2) 
                        * (target_position - observerA_spacetime_traveled), 
                which accounts for the additional spacetime distance resulting from 
                Observer B's faster movement through spacetime.
                
            Press 'enter' to begin or "expand" once more for conceptual wrap'''

        elif level == 6:
            reset_activity_timer(360)
            self.newpage()
            intro_text = '''
    Final Conceptual of Code

        This program simulates the relativistic effects of gravity on spacetime by conceptually manipulating 
        a hypotenuse — representing the path or timeline towards a target point. The core mechanism is to 
        adjust the rate at which this hypotenuse is traversed, reflecting time dilation or contraction 
        experienced due to gravity.

        Observer A (Approaching Gravity):
            Mechanism: Each 'left' movement symbolizes a step towards a stronger gravitational field, 
                effectively 'stretching' spacetime.
            Calculation: The observerA_time_dilation_rate is determined by fitting the adjusted distance 
                to the target into the remaining distance along the hypotenuse. This effectively 'slows down' 
                the rate of traversal, simulating time dilation.
            Example: If the target is 10 units away and Observer A moves 'left', their perspective shifts to 
                being 10 units away again, but the rate at which they cover these units slows down. If they 
                were 1 unit away from the target and moved 'left', their new rate of 0.8181 (approx.) reflects 
                a slower progression, as now they need to fit 10 steps into what appears as 9 units, plus the 
                step taken.

        Observer B (Moving Away from Gravity):
            Mechanism: Conceptually, when Observer A moves 'left', Observer B is moving away from gravity, 
                experiencing spacetime 'contraction'.
            Calculation: The observerB_time_contraction_rate is the reciprocal of Observer A's rate, 
                indicating a quicker traversal of spacetime, as the distance to the target point stretches but 
                must still fit within the original distance.
            Example: If the target is 10 units away and Observer B's movement implies they are now 11 units 
                away, their progression rate increases. Their faster rate of 1.22222 means they cover more 
                ground in spacetime, fitting what is now perceived as 12.22222 units into the original 
                10-step journey towards the target.
        
        Press 'enter' to begin'''
            
        else:
            return  # Exit the function and continue with the rest of the program

        # Show the intro text for the current level
        user_input = input(f"{intro_text}\n> ")

        # If user types 'expand', recursively call the function with the next level
        if user_input.lower() == 'expand':
            self.show_intro(level + 1)
        else:
            return  # User typed something other than 'expand', so return and continue the program

    # Function to calculate the distance to B
    def calculate_distance(self, x, target_position):
        return abs(target_position - x)

    # Function to get correct initial integer for final point
    @staticmethod
    def get_positive_integer(prompt):
        while True:
            try:
                value = Decimal(input(prompt))
                if value > 0 and value == value.to_integral_value():
                    return value
                else:
                    print("Please enter a non-zero positive whole number.")
            except InvalidOperation:
                print("Invalid input. Please enter a valid number.")

    def main(self):
        self.show_intro()
        reset_activity_timer() # Reset for inactivity

        observer_position = Decimal('0') # Point A on x-observer_position
        target_position = self.get_positive_integer("Enter the point to reach (Non-zero Positive Integer): ")  # Point B on x-observer_position
        self.newpage()

        observerA_spacetime_traveled = Decimal('0')
        observerA_time_dilation_rate = Decimal('1')
        observerB_spacetime_traveled = Decimal('0')

        your_spacetime_traveled = Decimal('0')  # Total distance considering imaginary

        print("Note, each 'left' and 'right' YOU input is considered 1 unit per 1 second of traversal for yourself")
        print(f"Starting at: ({observer_position}, {0})")
        print(f"Getting to point: ({target_position}, {0})")
        print(f"Current shortest distance: {target_position - observer_position}")   

        while True:
            reset_activity_timer() # Reset for inactivity
            print()
            print("Input 'exit' to return to main Terminal.")
            move = input("Enter movement direction (l(add gravity)/r(natural flow forwards): ")
            if (move == 'exit'):
                break

            print()
            print("----------------------------------------------------------")

            # Update position based on input
            if move == 'l':
                observer_position -= Decimal('1')
            elif move == 'r':
                observer_position += Decimal('1')
            elif move == 'e':  # Exit condition
                break
            else:
                continue  # If the input is not recognized, continue to the next iteration of the loop

            curr_distance = self.calculate_distance(observer_position, target_position)

            # In the event of moving 'away' from point or 'decelerating'
            # '+1' accounts for the first step rate to avoid division by zero
            observerA_time_dilation_rate = (target_position - observerA_spacetime_traveled) / (curr_distance + Decimal('1'))
            #Flip perspective calculations
            observerB_time_contraction_rate = Decimal('1') / observerA_time_dilation_rate

            # Adds the rate to the distance for one unit of movement
            observerA_spacetime_traveled += observerA_time_dilation_rate
            # Flip real distance
            observerB_spacetime_traveled += observerB_time_contraction_rate

            # Final point for flipped perspective
            observerB_extended_target = observerB_spacetime_traveled + ((observerB_time_contraction_rate**Decimal('2')) * (target_position - observerA_spacetime_traveled))

            your_spacetime_traveled += Decimal('1')  # Increment total distance considering imaginary

            print("--- Your Spacetime Perspective ---")
            print(f"From your vantage point, observing spacetime unfold at a constant rate of 1 second per movement:")
            print(f"Convergence Point: ({target_position}, 0)")
            print(f"Your Current Coordinate: ({observer_position}, 0)")
            print(f"Dimensional Distance to Convergence: {curr_distance} units")
            print(f"Spacetime Passage: {your_spacetime_traveled} seconds")
            print()

            print("--- Observer A's Gravitational Journey ---")
            print(f"Observer A's convergence with stronger gravity alters their temporal flow:")
            print(f"Target Convergence: {target_position} units")
            print(f"Time Dilation Rate: {observerA_time_dilation_rate:.10f} (slower time perception)")
            print(f"Spacetime Traversed: {observerA_spacetime_traveled:.20f} units")
            print()

            print("--- Observer B's Escape from Gravity ---")
            print(f"Observer B's journey away from gravity affects their temporal experience:")
            print(f"Extended Convergence Point: {observerB_extended_target:.5f} units")
            print(f"Time Contraction Rate: {observerB_time_contraction_rate:.5f} (accelerated time perception)")
            print(f"Spacetime Traversed: {observerB_spacetime_traveled:.5f} units")

            if observer_position == target_position:
                reset_activity_timer() # Reset for inactivity
                print("\nYou've reached the convergence point in spacetime!")
                print("\n--- Journey Recap ---")
                print(f"Throughout your journey spanning {your_spacetime_traveled} seconds:")
                print(f"Observer A (approaching gravity) experienced a passage of {observerA_spacetime_traveled:.5f} seconds/units.")
                print(f"Observer B (receding from gravity) navigated through {observerB_spacetime_traveled:.5f} seconds/units.")
                print("\n--- Relative Time Flow ---")
                print(f"From your vantage point in spacetime, each temporal unit (second/spatial unit) for you corresponded to:")
                print(f"{observerA_time_dilation_rate:.5f} seconds for Observer A, illustrating the dilation of time near stronger gravity.")
                print(f"{observerB_time_contraction_rate:.5f} seconds for Observer B, reflecting the contraction of time as gravity lessens.")
                print("\nThis encapsulation showcases the relativity of time and space as influenced by gravity,")
                print("demonstrating how each observer's traversal through spacetime varies from their unique perspective.")
                print()

                break

    def run(self):
        self.main()
        return "exit_to_main"


# t' = t * sqrt(1-(2GM/rc^2)) general relativity

# t' = t * sqrt(1 - (v^2 / c^2)) special relativity
    
# g = GM/r^2
    
# g = (c^2/2r)(1-(t'/t)^2)
    
# M = (rc^2/2G)((t')^2 - 1)
    
