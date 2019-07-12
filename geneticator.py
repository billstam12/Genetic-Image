from deap import base, creator, tools, algorithms
from random import randint, random, gauss
from PIL import Image, ImageDraw, ImageTk, ImageGrab
from functools import partial
from math import sqrt
import numpy as np
import Tkinter  as tk


test_image = Image.open("test_image.jpg")
SIZE = 100
NUMBER_OF_TRIANGLES = 50
POPULATION = 300
NGEN = 1000
POLY = 3
CXPB = 0.5
MUTPB = 0.1

def get_canvas_coordinates(cv):
		
        x = cv.winfo_rootx()+cv.winfo_x()
        y = cv.winfo_rooty()+cv.winfo_y()
        x1 = x + cv.winfo_width()
        y1 = y + cv.winfo_height()
        box = (x, y, x1, y1)
        return box
		
def gen_one_triangle():
	return (tuple ([(randint(0,SIZE), randint(0,SIZE)) for i in xrange(POLY)]),
			randint(0,255), randint(0, 255), randint(0, 255), randint(0,30))
			
def triangles_to_image(triangles):
	im = Image.new('RGB', (SIZE, SIZE), (255,255,255))

	for tri in triangles:
		mask = Image.new("RGBA", (SIZE, SIZE))
		draw = ImageDraw.Draw(mask)
		draw.polygon(tri[0], fill = tri[1:])
		im.paste(mask, mask=mask)
		del mask, draw
	return im
	
# Genetic Functions
def evaluate(im1, t2):
	im2 = triangles_to_image(t2)
	pix1, pix2 = im1.load(), im2.load()
	ans = 0
	for i in xrange(SIZE):
		for j in xrange(SIZE):
			a1, a2, a3 = pix1[i, j]
			b1, b2, b3 = pix2[i, j]
			ans += (a1 - b1) ** 2 + (a2 - b2) ** 2 + (a3 - b3) ** 2
	return 1 - (1. * sqrt(ans) / sqrt(SIZE * SIZE * 3 * 255 * 255)),


def mutate(triangles):
	e0 = evaluate(test_image, triangles)
	for i in xrange(10):
		tid = randint(0, NUMBER_OF_TRIANGLES - 1)
		oldt = triangles[tid]

		t = list(oldt)
		p = randint(0, 2 * POLY + 4 - 1)
		if p < 2 * POLY:
			points = list(t[0])
			pnt = list(points[p / 2])
			pnt[p%2] = max(0, min(SIZE, gauss(pnt[p%2], 10)))
			#pnt[p % 2] = randint(0, SIZE)
			points[p / 2] = tuple(pnt)
			t[0] = tuple(points)
		else:
			p -= 2 * POLY - 1
			t[p] = max(0, min(255, int(gauss(t[p], 20))))
			#t[p] = randint(0, 255)
			
		triangles[tid] = tuple(t)
		if evaluate(test_image, triangles) > e0:
			break
		else:
			triangles[tid] = oldt
	return (triangles,)
	
	
creator.create("Fitness", base.Fitness, weights = (1.0,)) #Maximize similarity
creator.create("Individual", list, fitness=creator.Fitness)

"""
Basically the following lines will create a population comprised by individuals each with 50 triangles
"""

toolbox  = base.Toolbox()
toolbox.register("attr", gen_one_triangle)
toolbox.register("individual", tools.initRepeat, creator.Individual, toolbox.attr, NUMBER_OF_TRIANGLES)
toolbox.register("population", tools.initRepeat, list, toolbox.individual)

toolbox.register("evaluate", partial(evaluate, test_image))
toolbox.register("mate", tools.cxTwoPoint)
toolbox.register("mutate", mutate)
toolbox.register("select", tools.selTournament, tournsize=3)

def main():
	pop = toolbox.population(n = POPULATION)
	hof = tools.HallOfFame(1)
	
	stats = tools.Statistics(lambda ind: ind.fitness.values)
	stats.register("std", np.std)
	stats.register("max", np.max)
	stats.register("avg", np.mean)
	stats.register("min", np.min)
	top = tk.Tk()
	C = tk.Canvas(top, bg="white", height=500, width=500)
	C.image1 = ImageTk.PhotoImage(Image.open("test_image.jpg"))
	im = C.create_image(50,200, image = C.image1, anchor = "nw")
	C.pack()
	g = 0
	C.gen_text = C.create_text(250, 50, text = "Generation " + str(0) ) 
	C.min_text = C.create_text(250, 100, text = "  Min " + str(0))
	C.max_text = C.create_text(250, 120, text = "  Max " + str(0))
	C.mean_text = C.create_text(250, 140, text = "  Avg " + str(0))
	C.std_text = C.create_text(250, 160, text = "  Std " + str(0))
	

	while g < NGEN:
		g = g + 1
		print("-- Generation %i --" % g)
		offspring = toolbox.select(pop, len(pop))
		offspring = list(map(toolbox.clone, offspring))
		for child1, child2 in zip(offspring[::2], offspring[1::2]):
			if random() < CXPB:
				toolbox.mate(child1, child2)
				del child1.fitness.values
				del child2.fitness.values

		for mutant in offspring:
			if random() < MUTPB:
				toolbox.mutate(mutant)
				del mutant.fitness.values
				
		# Evaluate the individuals with an invalid fitness
		invalid_ind = [ind for ind in offspring if not ind.fitness.valid]
		fitnesses = map(toolbox.evaluate, invalid_ind)
		for ind, fit in zip(invalid_ind, fitnesses):
			ind.fitness.values = fit
			
		pop[:] = offspring
		# Gather all the fitnesses in one list and print the stats
		fits = [ind.fitness.values[0] for ind in pop]
        
		# Get best individual
		best = pop[np.argmax(ind.fitness.values[0] for ind in pop)]
		
		length = len(pop)
		mean = sum(fits) / length
		sum2 = sum(x*x for x in fits)
		std = abs(sum2 / length - mean**2)**0.5
        
		#print("  Min %s" % min(fits))
		#print("  Max %s" % max(fits))
		#print("  Avg %s" % mean)
		#print("  Std %s" % std)
		#open('result.txt', 'w').write(repr(best))
		#triangles_to_image(best).save('generations/generation_' + str(g) + '.bmp')
		C.itemconfigure(C.gen_text, text = "Generation " + str(g)) 
		C.itemconfigure(C.min_text, text = "  Max " + str(max(fits)))
		C.itemconfigure(C.max_text, text = "  Min " + str(min(fits)))
		C.itemconfigure(C.mean_text, text = "  Mean " + str(mean))
		C.itemconfigure(C.std_text, text = "  Std " + str(std))
		
		C.image2 = ImageTk.PhotoImage(triangles_to_image(best))
		im = C.create_image(350,200, image = C.image2, anchor = "nw")
		ImageGrab.grab(bbox = get_canvas_coordinates(C)).save("generations/generation_" + str(g) + ".bmp")
        
		C.update()

		
		
		
	"""
	pop, log = algorithms.eaSimple(
		pop, toolbox, cxpb=CXPB, mutpb=MUTPB, ngen=NGEN, stats=stats,
		halloffame=hof, verbose=True)
	"""
	
		

if __name__ == '__main__':
	main()





