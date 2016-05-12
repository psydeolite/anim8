"""========== script.py ==========

  This is the only file you need to modify in order
  to get a working mdl project (for now).

  my_main.c will serve as the interpreter for mdl.
  When an mdl script goes through a lexer and parser, 
  the resulting operations will be in the array op[].

  Your job is to go through each entry in op and perform
  the required action from the list below:

  frames: set num_frames for animation

  basename: set name for animation

  vary: manipluate knob values between two given frames
        over a specified interval

  set: set a knob to a given value
  
  setknobs: set all knobs to a given value

  push: push a new origin matrix onto the origin stack
  
  pop: remove the top matrix on the origin stack

  move/scale/rotate: create a transformation matrix 
                     based on the provided values, then 
		     multiply the current top of the
		     origins stack by it.

  box/sphere/torus: create a solid object based on the
                    provided values. Store that in a 
		    temporary matrix, multiply it by the
		    current top of the origins stack, then
		    call draw_polygons.

  line: create a line based on the provided values. Store 
        that in a temporary matrix, multiply it by the
	current top of the origins stack, then call draw_lines.

  save: call save_extension with the provided filename

  display: view the image live
  
  jdyrlandweaver
  ========================="""



import mdl
from display import *
from matrix import *
from draw import *
from os import mkdir

"""======== first_pass( commands, symbols ) ==========

  Checks the commands array for any animation commands
  (frames, basename, vary)
  
  Should set num_frames and basename if the frames 
  or basename commands are present

  If vary is found, but frames is not, the entire
  program should exit.

  If frames is found, but basename is not, set name
  to some default value, and print out a message
  with the name being used.

  jdyrlandweaver
  ==================== """
def first_pass( commands ):
    #print commands
    num_frames=None
    basename=None
    vary=None
    #look for animation commands
    for command in commands:
        #0 is cmd itself, rest are args
        if command[0]=='vary' and num_frames==None:
            print "Must set frames before varying"
            return
        elif command[0]=='frames':
            num_frames=command[1]
        elif command[0]=='basename':
            basename=command[1]
    if basename==None:
        print 'Using name DEFAULT as basename'
        basename='DEFAULT'
    return [num_frames, basename]

"""======== second_pass( commands ) ==========

  In order to set the knobs for animation, we need to keep
  a seaprate value for each knob for each frame. We can do
  this by using an array of dictionaries. Each array index
  will correspond to a frame (eg. knobs[0] would be the first
  frame, knobs[2] would be the 3rd frame and so on).

  Each index should contain a dictionary of knob values, each
  key will be a knob name, and each value will be the knob's
  value for that frame.

  Go through the command array, and when you find vary, go 
  from knobs[0] to knobs[frames-1] and add (or modify) the
  dictionary corresponding to the given knob with the
  appropirate value. 
  ===================="""
def second_pass( commands, num_frames ):
    knobs=[]
    for i in range(num_frames):
        knobs.append({})
        
    #for frame in range(num_frames):
    for command in commands:
            #print command
        if command[0]=='vary':
            #c_frame={}
            for i in range(num_frames):
            #key: knob name; value: knob value
                frame_start=command[2]
                frame_end=command[3]
                val_start=command[4]
                val_end=command[5]
                knob_name=command[1]
                knob_val=1 #temp
                if i<frame_start: #animation hasn't started yet
                    #c_frame[knob_name]=val_start
                    knobs[i][knob_name]=val_start
                elif i>frame_end: #animation already ended
                    knobs[i][knob_name]=val_end
                else:
                    knob_val = val_start + ( (val_end - val_start)*(i - frame_start) / float((frame_end - frame_start)))
                    knobs[i][knob_name]=knob_val
                #c_frame[knob_name]=knob_val
                #print c_frame
                #knobs.append(c_frame)
    print knobs
    return knobs

def run(filename):
    """
    This function runs an mdl script
    """
    color = [255, 255, 255]
    tmp = new_matrix()
    ident( tmp )

    p = mdl.parseFile(filename)

    if p:
        (commands, symbols) = p
    else:
        print "Parsing failed."
        return

   
    screen=new_screen()
    pass1=first_pass(commands)
    num_frames=pass1[0]
    basename=pass1[1]
    anim=False
    
    if num_frames==None:
        print 'Not animated'
        num_frames=1
    else:
        print 'Animated'
        knobs=second_pass(commands, num_frames)
        anim=True
        print knobs
    mkdir(basename, 0755)
        
    #time to iterate through the framezzz
    for i in range(num_frames):
        #print 'start'
        stack = [ tmp ]
        #screen = new_screen()    
        
        for command in commands:
            #print commands
            if command[0] == "pop":
                stack.pop()
                if not stack:
                    stack = [ tmp ]
                    
            if command[0] == "push":
                stack.append( stack[-1][:] )

            if command[0] == "save":
                save_extension(screen, command[1])

            if command[0] == "display":
                display(screen)

            if command[0] == "sphere":
                m = []
                add_sphere(m, command[1], command[2], command[3], command[4], 5)
                matrix_mult(stack[-1], m)
                draw_polygons( m, screen, color )

            if command[0] == "torus":
                m = []
                add_torus(m, command[1], command[2], command[3], command[4], command[5], 5)
                matrix_mult(stack[-1], m)
                draw_polygons( m, screen, color )

            if command[0] == "box":                
                m = []
                add_box(m, *command[1:])
                matrix_mult(stack[-1], m)
                draw_polygons( m, screen, color )

            if command[0] == "line":
                m = []
                add_edge(m, *command[1:])
                matrix_mult(stack[-1], m)
                draw_lines( m, screen, color )
                
            if command[0] == "bezier":
                m = []
                add_curve(m, command[1], command[2], command[3], command[4], command[5], command[6], command[7], command[8], .05, 'bezier')
                matrix_mult(stack[-1], m)
                draw_lines( m, screen, color )

            if command[0] == "hermite":
                m = []
                add_curve(m, command[1], command[2], command[3], command[4], command[5], command[6], command[7], command[8], .05, 'hermite')
                matrix_mult(stack[-1], m)
                draw_lines( m, screen, color )

            if command[0] == "circle":
                m = []
                add_circle(m, command[1], command[2], command[3], command[4], .05)
                matrix_mult(stack[-1], m)
                draw_lines( m, screen, color )

                     
            if command[0] == "move":
                '''val=1
                knob_name=command[-1]
                if knob_name!=None:
                    val=knobs[i][knob_name]'''
                xval = command[1] 
                yval = command[2] 
                zval = command[3] 

                try:
                    if len(command) == 5:
                        xval*=knobs[i][command[4]]
                        yval*=knobs[i][command[4]]
                        zval*=knobs[i][command[4]]
                except:
                    pass
                t = make_translate(xval, yval, zval)
                matrix_mult( stack[-1], t )
                stack[-1] = t

            if command[0] == "scale":
                ''' val=1
                knob_name=command[-1]
                if knob_name!=None:
                    #print 'hi'
                    #print knobs[i]
                    #print knob_name
                    val=knobs[i][knob_name]
                xval = command[1] * val
                yval = command[2] * val
                zval = command[3] * val'''

                xval = command[1] 
                yval = command[2] 
                zval = command[3] 

                try:
                    if len(command) == 5:
                        xval*=knobs[i][command[4]]
                        yval*=knobs[i][command[4]]
                        zval*=knobs[i][command[4]]
                except:
                    pass

                t = make_scale(xval, yval, zval)
                matrix_mult( stack[-1], t )
                stack[-1] = t
                
            if command[0] == "rotate":
                #print 'rot'
                '''val=1
                knob_name=command[-1]
                if knob_name!=None:
                    val=knobs[i][knob_name]
                angle = command[2] * (math.pi / 180) * val'''
                angle=command[2] * (math.pi / 180)
                try:
                    if len(command)==4:
                        angle*=knobs[i][commands[3]]
                except:
                    pass

                if command[1] == 'x':
                    t = make_rotX( angle )
                elif command[1] == 'y':
                    t = make_rotY( angle )
                elif command[1] == 'z':
                    t = make_rotZ( angle )            
                    
                matrix_mult( stack[-1], t )
                stack[-1] = t
          
            '''if anim:
                save_extension(screen, basename+'/' + basename+'%04d.png' % i)
            clear_screen(screen)
            print i'''
            if i==0:
                save_ppm(screen,basename+"/"+basename+'00'+str(i)+".ppm")
            else:
                z = 2-int(math.log10(i))              
                save_ppm(screen,basename+"/"+basename+'0'*z+str(i)+".ppm")        
                clear_screen(screen)     
            print i

