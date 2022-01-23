from which_pyqt import PYQT_VER
if PYQT_VER == 'PYQT5':
	from PyQt5.QtCore import QLineF, QPointF, QObject
elif PYQT_VER == 'PYQT4':
	from PyQt4.QtCore import QLineF, QPointF, QObject
else:
	raise Exception('Unsupported Version of PyQt: {}'.format(PYQT_VER))



import time

# Some global color constants that might be useful
RED = (255,0,0)
GREEN = (0,255,0)
BLUE = (0,0,255)

# Global variable that controls the speed of the recursion automation, in seconds
#
PAUSE = 0.25

#
# This is the class you have to complete.
#
class ConvexHullSolver(QObject):

# Class constructor
	def __init__( self):
		super().__init__()
		self.pause = False
		
# Some helper methods that make calls to the GUI, allowing us to send updates
# to be displayed.

	def showTangent(self, line, color):
		self.view.addLines(line,color)
		if self.pause:
			time.sleep(PAUSE)

	def eraseTangent(self, line):
		self.view.clearLines(line)

	def blinkTangent(self,line,color):
		self.showTangent(line,color)
		self.eraseTangent(line)

	def showHull(self, polygon, color):
		self.view.addLines(polygon,color)
		if self.pause:
			time.sleep(PAUSE)
		
	def eraseHull(self,polygon):
		self.view.clearLines(polygon)
		
	def showText(self,text):
		self.view.displayStatusText(text)
	

# This is the method that gets called by the GUI and actually executes
# the finding of the hull
	def compute_hull( self, points, pause, view):
		self.pause = pause
		self.view = view
		assert( type(points) == list and type(points[0]) == QPointF )

		t1 = time.time()
		# TODO: SORT THE POINTS BY INCREASING X-VALUE
		points = sorted(points, key=lambda point: point.x())
		t2 = time.time()

		t3 = time.time()

		hullPoints = self.ConvexHullSolver(points)
		# this is a dummy polygon of the first 3 unsorted points
		polygon = [QLineF(hullPoints[i],hullPoints[(i+1)%len(hullPoints)]) for i in range(len(hullPoints))]
		# TODO: REPLACE THE LINE ABOVE WITH A CALL TO YOUR DIVIDE-AND-CONQUER CONVEX HULL SOLVER
		
		t4 = time.time()

		# when passing lines to the display, pass a list of QLineF objects.  Each QLineF
		# object can be created with two QPointF objects corresponding to the endpoints
		self.showHull(polygon,RED)
		self.showText('Time Elapsed (Convex Hull): {:3.3f} sec'.format(t4-t3))

#---------------------------- MY STUFF -------------------------------------
	#---------------- HELPER FUNCTIONS ---------------------------

	def FindSlope(self,p,q):
		num = (q.y() - p.y())
		denom = (q.x() - p.x())
		if denom != 0:
			return num / denom
		return 0

	def CounterClockNeighbor(self, point, sortedHull):
		#if there is more than one element in the hull
		if len(sortedHull) > 1:
			#if the pont is the first element in the array, then return last element
			if sortedHull.index(point) == 0:
				return sortedHull[len(sortedHull) - 1]
			#else return the element before 'point'
			else:
				return sortedHull[sortedHull.index(point) - 1]
		#if there is only one element in the hull
		else:
			return point

	def ClockwiseNeighbor(self, point, sortedHull):
		#if there is more than one element in the hull
		if len(sortedHull) > 1:
			#if the point is the last element in the array, then return 1st element
			if sortedHull.index(point) == len(sortedHull) - 1:
				return sortedHull[0]
			#else return the element after 'point' in the array
			else:
				return sortedHull[sortedHull.index(point) + 1]
		#if there is only one element in the hull
		else:
			return point

	def CombineHulls(self, LH, RH, UT, LT):
		hull = []
		point = UT[1]
		while point != LT[1]:
			hull.append(point)
			point = self.ClockwiseNeighbor(point,RH)
		hull.append(point)
		point = LT[0]
		while point != UT[0]:
			hull.append(point)
			point = self.ClockwiseNeighbor(point,LH)
		hull.append(point)
		return hull
				
	#---------------- END HELPER FUNCTIONS ---------------------------

	def FindUpperTangent(self, L,R):
		#find the rightmost point p in L and leftmost point q in R
		if len(L) == 1:
			p = L[0]
		#rightmost point is the last element in an array that is sorted by x value
		else:
			p = sorted(L, key=lambda point: point.x())[len(L) - 1]
		if len(R) == 1:
			q = R[0]
		#leftmost point is the first element in an array that is sorted by x value
		else:
			q = sorted(R, key=lambda point: point.x())[0]
		temp = (p,q)
		done = False
		while not done:
			done = True
			r = self.CounterClockNeighbor(p, L)
			# while temp is not upper tangent to L
			while self.FindSlope(temp[0], temp[1]) < self.FindSlope(r,q):
				temp = (r,q)
				p = r
				done = False
				r = self.CounterClockNeighbor(p, L)
			r = self.ClockwiseNeighbor(q,R)
			# while temp is not upper tangent to R
			while self.FindSlope(temp[0], temp[1]) > self.FindSlope(p,r):
				temp = (p,r)
				q = r
				done = False
				r = self.ClockwiseNeighbor(q,R)
		return temp


	def FindLowerTangent(self,L,R):
		# find the rightmost point p in L and leftmost point q in R
		if len(L) == 1:
			p = L[0]
		#rightmost point is the last element in an array that is sorted by x value
		else:
			p = sorted(L, key=lambda point: point.x())[len(L) - 1]
		if len(R) == 1:
			q = R[0]
		#leftmost point is the first element in an array that is sorted by x value
		else:
			q = sorted(R, key=lambda point: point.x())[0]
		temp = (p,q)
		done = False
		while not done:
			done = True
			r = self.ClockwiseNeighbor(p, L)
			# while temp is not lower tangent to L:
			while self.FindSlope(temp[0], temp[1]) > self.FindSlope(r,q):
				temp = (r,q)
				p = r
				done = False
				r = self.ClockwiseNeighbor(p, L)
			r = self.CounterClockNeighbor(q, R)
			# while temp is not lower tangent to R:
			while self.FindSlope(temp[0], temp[1]) < self.FindSlope(p,r):
				temp = (p,r)
				q = r
				done = False
				r = self.CounterClockNeighbor(q, R)
		return temp


	def ConvexHullSolver(self, points):
		n = len(points)
		hull = []
		if len(points) == 1:
			 hull.append(points[0])
			 return hull
		if len(points) > 1:
			LH = self.ConvexHullSolver(points[:n//2])
			RH = self.ConvexHullSolver(points[n//2:])
			UT = self.FindUpperTangent(LH, RH)
			LT = self.FindLowerTangent(LH, RH)
		return self.CombineHulls(LH,RH,UT,LT)
			

	