# circuitsim
This circuit simulation tool allows users to input potential difference, resistance, and voltage data across various components. It then processes this data, applying Depth-First Search (DFS) algorithms to automatically identify the circuit type.

## Technical Aspects
I will use an SQLite database for the authentication and will use Tkinter for the GUI. Depth-First Search will be utilised to find neighbouring nodes to identify whether the circuit is series, parallel or series parallel. This is needed to calculate potential difference, current and resistance. Python's built-in pacakge, 'json', will be used to reload circuits. Complex components such as thermistors are used along with Steinhart formula to convert temperature to resistance.

## Scenario 
Making electrical circuits physically requires a lot of equipment and time to connect components together. Some students may not have all the equipment to find out their desired outputs at home or at school. They may also want to test different outputs, but may want to restore older circuits but would have to remake them, spending more time.

## My solution
To solve this problem, this simulation allows the user to make their own circuit on this program, being able to connect components with much ease and convenience.

CircuitSim provides a wide range of electrical circuit components, which the student would be able to drag and drop into a simulation space to make their desired circuit. Components will react depending on the other components, for example, a light bulb would light up if there is a cell. The visuals would be simple with all the components being represented by their circuit symbols. The students can also find out values such as the potential difference values through voltmeters and ammeters after setting the values up. For more breadth, more components on the logical end such as AND gates are also usable for logic gate simulations.

Students will be able to access their account by entering their username, being able to load in circuits they have previously saved into the database using a save function. There will be a user interface which provides a vast list of electrical components which they can drag and drop into the simulation space, and the student would need to use wires to connect the component. Calculations will be carried out depending on if the circuit is in series or parallel to display the current, voltage and resistance of the circuit which will then be represented on a current-voltage graph (IV graph). The student may also be able to load in default, premade circuits as they wish which is provided by the program. The states of the components will constantly be updated for every change made to the circuit.
