# Animare
An application the transform written text into a 3D scene.
It's a python project that takes a text that describes a scene as it's input an creates a 3D scene.
the project can simulate a limited set of actions [sit, walk, talk, run, wave, hit, jump, cry, kick, dance, sleep] 
and limited set of objects [humans(boy,girl,man,woman,old man,old woman), chair , bed, ball, room, kitchen, piano, table, television, plate, food]

the model generation module is responsible for generating the necessary models and it's required deformation whither coloring or scaling.
the positing module is responsible for initial positing of the object based on the description.
the animation generator is responsible for generating the actions and it's animation an applying the simulating the scene physics an export the output video.