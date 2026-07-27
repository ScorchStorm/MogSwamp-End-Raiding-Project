import gspread
from matplotlib import pyplot as plt
from mpl_interactions import panhandler, zoom_factory
import numexpr as ne
import numpy as np

np.set_printoptions(precision = 7, suppress = True, linewidth = 170) # this is just my personal preference for how I like numpy to print numbers

# Change the file path below to match the file path of your waypoint file for Xaeros Minimap
waypoint_file = r'C:\Users\User\curseforge\minecraft\Instances\InstanceName\xaero\minimap\Multiplayer_play.flatnet.gg\dim%1\mw$default_1.txt'
n_waypoints = 12 # this is the default number of cities to display all at once because it's the most colors you can have in a rainbow sequence

def main():
    print('Click on the first end city you would like to raid')
    get_end_cities()
    choose_first_end_city()
    print(f'Congrats! You have raided all {n_cities} end cities!')

def get_end_cities():
    global n_cities
    n_cities = int(input('How many end cities would you like to raid? '))
    get_server_end_cities()
    if len(unraided_cities_x) < n_cities:
        print(f'Sorry, there are not enough unraided cities in the server spreadsheet to raid {n_cities} cities')
        print(f'Finding a path to raid all {len(unraided_cities_x)} unraided cities')
        n_cities = len(unraided_cities_x)

def get_server_end_cities(): # made with some help from Gemini
    global unraided_cities_x, unraided_cities_z, raided_cities_x, raided_cities_z, unraided_cities_row_indexes
    print('Getting coordinates from server spreadsheet')
    gc = gspread.service_account('credentials2.json')
    worksheet = gc.open_by_key('1SASg6rYtYl2TeVTvBCNOnW6IyzbBjSlzolsEil9JPZQ').sheet1
    rows = worksheet.get_all_values()[1:]
    unraided_cities_x, unraided_cities_z, raided_cities_x, raided_cities_z, unraided_cities_row_indexes = [], [], [], [], []
    for n in range(len(rows)):
        row = rows[n]
        if row[2] != '': # if the 3rd item in an end city's row is not blank, the city has been raided
            raided_cities_x.append(int(row[0]))
            raided_cities_z.append(int(row[1]))
        else:
            unraided_cities_x.append(int(row[0]))
            unraided_cities_z.append(int(row[1]))
            unraided_cities_row_indexes.append(n+2)
    print(f'The server spreadsheet has the coordinates of {len(unraided_cities_x)} unraided and {len(raided_cities_x)} raided end cities')

def choose_first_end_city():
    global fig, ax, ax2background
    plt.ioff()
    fig, ax = plt.subplots(1, 1, figsize=((6.5,6)))
    fig.canvas.mpl_connect('pick_event', click_city) # when you cick on an end city, this function is called, which helps find a path
    ax.set_aspect('equal')
    plt.xlabel("X-Axis")
    plt.ylabel("Z-Axis")
    max_x, min_x, max_z, min_z = max(unraided_cities_x), min(unraided_cities_x), max(unraided_cities_z), min(unraided_cities_z)
    border = (max_x - min_x + max_z - min_z)/150 + 500
    ax.scatter(unraided_cities_x, unraided_cities_z, [7 for _ in range(len(unraided_cities_x))], [[0,0,0] for _ in range(len(unraided_cities_z))], picker=True, label='unraided_cities')
    ax.scatter(raided_cities_x, raided_cities_z, [7 for _ in range(len(raided_cities_x))], [[1,0,0] for _ in range(len(raided_cities_x))], label = 'raided_cities')
    ax.plot([])
    ax.set(xlim=(min_x-border, max_x+border), ylim=(max_z+border, min_z-border))
    fig.canvas.draw()
    fig.canvas.manager.window.wm_geometry("+%d+%d" % (0, 0)) # move figure to top right of screen
    ax2background = fig.canvas.copy_from_bbox(ax.bbox)
    zoom_factory(ax)
    panhandler(fig)
    plt.title('Click on the First End City You Would Like to Raid')
    plt.legend()
    plt.show()

def click_city(event): # when you click on your first city, this function is called
    if event.mouseevent.button == 1:
        ind = event.ind
        first_city_x, first_city_z = unraided_cities_x[ind[0]], unraided_cities_z[ind[0]]
        print(f'You have picked your first city to be at {unraided_cities_x[ind[0]], unraided_cities_z[ind[0]]}')
        fig.clf()
        get_a_path(first_city_x, first_city_z) # this finds a path that you will use for end raiding
        timer = fig.canvas.new_timer(interval=10)
        timer.add_callback(plt.close)
        timer.start()

def get_a_path(first_city_x, first_city_z):
    global city_list, complex_cities
    limit = 2000 * n_cities ** 0.5 + 80 * n_cities
    max_x, min_x, max_z, min_z = first_city_x + limit, first_city_x - limit, first_city_z + limit, first_city_z - limit
    city_x, city_z, city_list, _ = closest_cities(max_x, min_x, max_z, min_z, unraided_cities_x, unraided_cities_z)
    make_distance_array()
    start_canvas(city_x, city_z, city_x, city_z)
    index_list, path_city_list = nearest_neighbor(city_list.index([first_city_x, first_city_z]))
    path_city_x, path_city_z = [c[0] for c in path_city_list], [c[1] for c in path_city_list]
    max_x, min_x, max_z, min_z = max(path_city_x), min(path_city_x), max(path_city_z), min(path_city_z)
    border = (max_x - min_x + max_z - min_z)/40 + 2000
    city_x, city_z, city_list, original_indexes = closest_cities(max_x+border, min_x-border, max_z+border, min_z-border, unraided_cities_x, unraided_cities_z)
    index_list = [city_list.index(city) for city in path_city_list]
    path_city_x, path_city_z = [c[0] for c in path_city_list], [c[1] for c in path_city_list]
    make_distance_array()
    city_array = np.array(city_list)
    complex_cities = city_array[:,0] + 1j*city_array[:,1]
    original_distance = find_total_distance(index_list)
    fig.clf()
    start_canvas(path_city_x, path_city_z, city_x, city_z, index_list)
    line1.set_data(extract_points(index_list))
    ax.draw_artist(line1)
    fig.canvas.blit(fig.bbox)
    fig.canvas.flush_events()
    tour = use_all_methods(index_list, original_distance)
    print(f"Coordinates of cities in path = {str([city_list[city] for city in tour])[1:-1].replace('[', '(').replace(']', ')')}")
    update_waypoints(tour, original_indexes)

def closest_cities(max_x, min_x, max_z, min_z, cities_x, cities_z, ignore_minimum=False):
    city_x = []
    city_z = []
    city_list = []
    original_indexes = []
    for n in range(len(cities_x)):
        if min_x < cities_x[n] < max_x and min_z < cities_z[n] < max_z:
            x = int(cities_x[n])
            z = int(cities_z[n])
            city_x.append(x)
            city_z.append(z)
            city_list.append([x, z])
            original_indexes.append(n)
    if ignore_minimum or (len(city_list) > 1.5*n_cities) or (len(city_list) == len(unraided_cities_x)):
        return city_x, city_z, city_list, original_indexes
    else: # the area we were looking in probably did not have enough unraided cities to make a well-optimized tour, so let's try again with a larger area
        return closest_cities(max_x+1000, min_x-1000, max_z+1000, min_z-1000, cities_x, cities_z)

def start_canvas(path_city_x, path_city_z, city_x, city_z, tour = []):
    global fig, ax, line1, line2, line3, line4, ax2background, suptitle, renderer, title_background
    ax = fig.add_subplot(1, 1, 1)
    suptitle = fig.suptitle(70*" "+"\n"+70*" ") # A long blank title that takes up two lines
    ax.set_aspect('equal')
    plt.xlabel("X-Axis")
    plt.ylabel("Z-Axis")
    line1, = ax.plot([])
    line2, = ax.plot([])
    line3, = ax.plot([])
    line4, = ax.plot([])
    max_x, min_x, max_z, min_z =  max(city_x), min(city_x), max(city_z), min(city_z)
    border = (max_x - min_x + max_z - min_z)/150 + 500
    o_city_x, o_city_z, _, _ = closest_cities(max_x, min_x, max_z, min_z, unraided_cities_x, unraided_cities_z)
    ax.plot(o_city_x, o_city_z, '.', color='lawngreen')
    ax.plot(path_city_x, path_city_z, 'k.')
    r_city_x, r_city_z, _, _ = closest_cities(max_x, min_x, max_z, min_z, raided_cities_x, raided_cities_z, True)
    ax.plot(r_city_x, r_city_z, 'r.')
    ax.set(xlim=(min_x - border, max_x + border,), ylim=(max_z + border, min_z - border))
    fig.canvas.manager.window.wm_geometry("+%d+%d" % (0, 0)) # move the figure to top right corner of the screen
    plt.show(block=False)
    renderer = fig.canvas.get_renderer()
    title_bbox = suptitle.get_window_extent(renderer=renderer).expanded(1.1, 1.3)
    fig.canvas.draw()
    title_background = fig.canvas.copy_from_bbox(title_bbox)
    if tour != []:
        suptitle.set_text("Initializing Canvas")
    else:
        suptitle.set_text("Running Nearest Neighbor Algorithm")
    ax2background = fig.canvas.copy_from_bbox(ax.bbox)
    fig.canvas.blit(title_bbox)
    fig.canvas.flush_events()

def make_distance_array():
    global A
    cities = np.array([city_list[n][0] + 1j*city_list[n][1] for n in range(len(city_list))])[:,np.newaxis]
    A = np.array(abs(cities.T-cities),float) # an array that records the distances from every point to every other point # you might also use numpy.linalg.norm 

def nearest_neighbor(i):
    A_new = A.copy()
    tour = [i]
    for _ in range(n_cities-1):
        A_new[:,i] = np.inf
        i = np.argmin(A_new[i]) # find the index of the nearest city
        tour.append(i)
        draw_nearest_neighbor(tour[:-1], tour[-2:])
    return tour, [city_list[n] for n in tour]

def draw_nearest_neighbor(blue_line, red_line):
    line1.set_data(extract_points(blue_line))
    fig.canvas.restore_region(ax2background)
    ax.draw_artist(line1)
    line2.set_data(extract_points(red_line))
    line2.set_color('red')
    ax.draw_artist(line2)
    fig.canvas.blit(ax.bbox)
    fig.canvas.flush_events()

def draw_tour(new_shortest_distance, original_distance, algorithm_name, blue_line, first_red_segment = None, second_red_segment = None, third_red_segment = None):
    fig.canvas.restore_region(ax2background)
    line1.set_data(extract_points(blue_line))
    ax.draw_artist(line1)
    if first_red_segment != None:
        line2.set_data(extract_points(first_red_segment))
        line2.set_color('red')
        ax.draw_artist(line2)
    if second_red_segment != None:
        line3.set_data(extract_points(second_red_segment))
        line3.set_color('red')
        ax.draw_artist(line3)
    if third_red_segment != None:
        line4.set_data(extract_points(third_red_segment))
        line4.set_color('red')
        ax.draw_artist(line4)
    update_title(new_shortest_distance, original_distance, algorithm_name)

def extract_points(list):
    list_x = [city_list[city][0] for city in list]
    list_z = [city_list[city][1] for city in list]
    return list_x, list_z

def update_title(new_shortest_distance, original_distance, algorithm_name):
    new_title = f'Distance = {new_shortest_distance:.3f}, Improvement = {(100*(original_distance - new_shortest_distance)/original_distance):.2f}%\nCurrent Algorithm: {algorithm_name}'
    draw_title(new_title)

def draw_title(new_title):
    fig.canvas.restore_region(title_background)
    suptitle.set_text(new_title)
    suptitle.draw(renderer)
    fig.canvas.blit(fig.bbox)
    fig.canvas.flush_events()

def find_total_distance(tour): # find the total distance of a tour
    cities = complex_cities[tour]
    return np.sum(abs(cities[1:]-cities[:-1])) # suprisingly, this is actually the fastest way I've found so far to calculate the length of a tour

def to_ordinal_num(n): # from: Thad Guidry
    return str(n) + {1: 'st', 2: 'nd', 3: 'rd'}.get(4 if 10 <= n % 100 < 20 else n % 10, "th")

def use_all_methods(tour, original_distance): # This function controls which algorithms the program uses. Some get less efficient as the number of end cities you want to raid increases
    loop_number = 1
    create_masks()
    n_changes = {'Flip Segments': 1, 'Move Segments': 1, 'Add New Points': 1}
    all_methods = {'Flip Segments': flip_segments, 'Move Segments': move_segments, 'Add New Points': add_new_points}
    while True:
        for method in all_methods:
            current_distance = find_total_distance(tour)
            if sum(n_changes.values()) - n_changes[method] != 0 or loop_number == 1:
                update_title(current_distance, original_distance, method)
                print(f'\nStarting {method} algorithm for the {to_ordinal_num(loop_number)} time')
                tour, n_changes[method] = all_methods[method](tour, original_distance, current_distance)
                if n_changes[method] == 0:
                    print(f'No shorter paths found using {method} algorithm')
            else:
                print('\nPath optimization complete\n')
                draw_title(f'Distance = {current_distance:.3f}, Improvement = {(100*(original_distance - current_distance)/original_distance):.2f}%\nOptimization Completed')
                return tour
        loop_number += 1

def create_masks():
    global mask_2D, mask_3D
    ones_2D = np.ones((n_cities, n_cities))
    mask_2D = np.triu(ones_2D, k=1)
    s, i, n = np.ogrid[:n_cities, :n_cities, :n_cities]
    condition = "((n-s+2 >= 0) & (-s+i-1 >= 0) | (n-s+2 <= 0) & (-s+i-1 <= 0) | (n-s+2 == 0) | (-s+i-1 == 0)) & (i<=n)"
    mask_3D = ne.evaluate(condition)

def flip_segments(tour, original_distance, predicted_distance): # This function will create a distance array that will calculate the change in distance for each value of i and n and choose the highest values
    f = len(tour) - 1
    n_changes = 0
    while True: # This will repeat until the loop is broken when val_max < 0
        A_new = np.take(np.take(A, tour, axis=0), tour, axis=1)
        vec = np.diagonal(A_new,1) # a matrix that records the distances from every point to the next point
        dist_old_1 = np.append(vec,0).reshape(1,n_cities)
        dist_old_2 = np.append(0,vec).reshape(n_cities,1)
        dist_new_1 = np.append(np.zeros((1,n_cities)),A_new,0)[:-1,:]
        dist_new_2 = np.append(A_new,np.zeros((A_new.shape[1],1)),1)[:,1:]
        slc = ne.evaluate("mask_2D*(dist_old_1 + dist_old_2 - dist_new_1 - dist_new_2)")
        i, n = np.unravel_index(np.argmax(slc), np.shape(slc)) # find the location of the change that will shorten the path the most
        val_max = slc[i][n] # find the segment flips (the values of i and n) that will make the greatest change to shorten your tour
        if val_max > 1e-11: # This was set to 0 instead of 1e-11, but then the code got stuck in an infinite loop of doing nothing
            tour = tour[:i]+tour[i:n+1][::-1]+tour[n+1:] # have it actively change the line while the loop is running
            predicted_distance -= val_max # predict the length of the tour given the change in length predicted by our array
            predicted_distance = check_predictions(tour, predicted_distance, True) # check whether the array's predictions are true, and update the distance
            n_changes += 1
            if i != 0 and n != f: # plot the new tour
                draw_tour(predicted_distance, original_distance, "Flip Segments", tour, [tour[i-1], tour[i]], [tour[n], tour[n+1]])
            else:
                draw_tour(predicted_distance, original_distance, "Flip Segments", tour)
        else: # if there are no changes the algorithm can make that will make the tour shorter
            return tour, n_changes

def move_segments(tour, original_distance, predicted_distance): # This function will create a distance array that will calculate the change in distance for each value of i, n and s and choose the highest values
    f = len(tour) - 1
    n_changes = 0
    while True:
        A_new = A[tour][:,tour] # rearranges the distance array for every segment flip
        dist_in = np.zeros((1, n_cities, n_cities))
        dist_in[0,1:,:-1] = A_new[:-1,1:] # the distance dependent only on i and s
        dist_ns = A_new[np.newaxis].transpose(1, 0, 2) # the distance dependent only on n and s
        dist_is = np.zeros((1, n_cities, n_cities))
        dist_is[0,:,1:] = A_new[:, :-1]
        dist_is = np.transpose(dist_is, (2, 1, 0)) # the distance dependent only on i and s
        vec = np.diagonal(A_new, offset=1)[np.newaxis, np.newaxis, :] # dependent on i and n # a matrix that records the distances from every point to the next point
        dist_i = np.rollaxis(np.insert(vec,0,0,axis=2),2,1) # the distance change dependent only on i
        dist_s = np.swapaxes(np.insert(vec,0,0,axis=2),0,2) # the distance change dependent only on s
        dist_n = np.insert(vec,f,0, axis=2) # the distance change dependent only on n
        dists_1 = ne.evaluate("(dist_s - dist_is)") # the distance dependent on i and/or s
        dists_2 = ne.evaluate("(dist_i + dist_n - dist_in)") # the distance dependent on i and/or n
        dists_3 = ne.evaluate("-dist_ns") # the distance dependent on n and/or s
        msc = ne.evaluate("mask_3D*(dists_1 + dists_2 + dists_3)") # this is repetitive, each change is represented exactly 2 times
        s, i, n = np.unravel_index(np.argmax(msc), np.shape(msc)) # find the location of the change that will shorten the path the most
        val_max = msc[s][i][n]
        if val_max > 1e-11: # This was set to 0 instead of 1e-11, but then the code got stuck in an infinite loop of doing nothing
            if i > n or i < s < n: # if s is between i and n or if i is larger than than n, then the change is invalid
                print('You have attempted to make an invalid change!') # let the user know the change was invalid
                break # stop the loop
            elif s < i: # if s < i, then the tour can be rearranged and sliced this way:
                tour = tour[:s]+tour[i:n+1]+tour[s:i]+tour[n+1:] # have it actively change the line while the loop is running
            elif i < s: # if i < s, then the tour can be rearranged and sliced this way:
                tour = tour[:i]+tour[n+1:s]+tour[i:n+1]+tour[s:] # have it actively change the line while the loop is running
            predicted_distance -= val_max # predict the length of the tour given the change in length predicted by our array
            predicted_distance = check_predictions(tour, predicted_distance, True) # check whether the array's predictions are true, and update the distance
            n_changes += 1
            if i != 0 and n != f and s != 0: # plot the new tour
                draw_tour(predicted_distance, original_distance, "Move Segments", tour, [tour[i-1], tour[i]], [tour[n], tour[n+1]], [tour[s-1], tour[s]])
            else:
                draw_tour(predicted_distance, original_distance, "Move Segments", tour)
            tour, _ = flip_segments(tour, original_distance, predicted_distance) # this calls the flip_segments function to see if it can make any quick positive changes before move_segments gives it another go
            predicted_distance = find_total_distance(tour) # update the current length of the tour
        else: # if there are no changes the algorithm can make that will make the tour shorter
            return tour, n_changes

def add_new_points(tour, original_distance, predicted_distance):
    if len(unraided_cities_x) == n_cities:
        print(f'No unraided cities could be added to the path because all unraided cities are already on the path')
        return tour, 0
    f = len(tour) - 1 # index of final point
    n_changes = 0
    while True:
        other_points = [point for point in range(len(city_list)) if point not in tour]
        A_new = np.zeros((len(tour)+2, len(other_points)))
        A_new[1:-1,:] = np.array(A)[tour][:,other_points]
        vec = np.zeros((len(tour)+1,1))
        vec[1:-1,:] = np.diagonal(np.array(A)[tour][:,tour], offset=1)[:,np.newaxis]
        dist_s1 = (vec[1:,:] + vec[:-1,:])[:,np.newaxis]
        a = -np.diagonal(np.array(A)[tour][:,tour], offset=2)[:,np.newaxis,np.newaxis]
        dist_s2 = np.insert(a,[0,len(a)],0,axis=0)
        dist_s = dist_s1 + dist_s2 # the distance dependent on s
        dist_n = np.transpose(vec[np.newaxis,1:,:], (2,0,1)) # the distance dependent on n
        dist_in = np.transpose(-A_new[2:,:,np.newaxis]-A_new[1:-1,:,np.newaxis], (2,1,0)) # the distance dependent on i and n
        msc = ne.evaluate("dist_s + dist_n + dist_in") # an array of the changes in distance
        diagonals = -A_new[2:,:] - A_new[:-2,:] + vec[1:,:] + vec[:-1,:]
        for s_ind in range(len(tour)):
            msc[s_ind,:,s_ind] = diagonals[s_ind,:]
            if s_ind !=0:
                msc[s_ind,:,s_ind-1] = diagonals[s_ind,:]
        s_ind, i_ind, n_ind = np.unravel_index(np.argmax(msc), np.shape(msc)) # find the location of the change that will shorten the path the most
        val_max = msc[s_ind][i_ind][n_ind] # find the segment flips (the values of i and n) that will make the greatest change to shorten your tour
        if val_max > 1e-11: # This was set to 0 instead of 1e-11, but then the code got stuck in an infinite loop of doing nothing
            s = tour[s_ind]
            tour.insert(n_ind+1, other_points[i_ind])
            tour.remove(s)
            predicted_distance -= val_max # predict the length of the tour given the change in length predicted by our array
            predicted_distance = check_predictions(tour, predicted_distance, True) # check whether the array's predictions are true, and update the distance
            n_changes += 1
            if n_ind-1 >= 0 and n_ind+1 <= f: # plot the new tour
                draw_tour(predicted_distance, original_distance, "Add New Points", tour, [tour[n_ind-1],tour[n_ind],tour[n_ind+1]])
            else:
                draw_tour(predicted_distance, original_distance, "Add New Points", tour)
        else: # if there are no changes the algorithm can make that will make the tour shorter
            return tour, n_changes
        
def check_predictions(tour, predicted_distance, if_print): # verify if the predictions made by the distance matrix are accurate
    actual_distance = find_total_distance(tour) # calculate the actual length of the tour
    error = abs(predicted_distance - actual_distance)
    if error > 1.87e-9: # if the change in the tour length is larger than the allowable error
        print(f'The change in distance was not exactly what we expected it to be!')  # print in the terminal if the error in predicted distance is greater than the error tolerance
        print(f'predicted_distance - actual_distance = {predicted_distance - actual_distance}') # print the value of the error in predicted distance
    elif if_print: # if if_print = True, tell the user if the predicted distance is correct
        print(f'Congrats! We found a new shorter path with a distance of {actual_distance}') # print in the terminal to let the user know that a shorter path has been found! =D
    return actual_distance # return the value of the actual distance for use in future calculations

def correct_starting_point(tour): # this isn't currently being used
    distance_to_start = abs(tour[0])
    distance_to_end = abs(tour[len(tour)-1])
    if distance_to_start > distance_to_end:
        return tour[::-1]

def update_waypoints(tour, original_indexes): # this functions updates the waypoints as users tell the program that they have visited the cities
    first_waypoint_rows = get_first_waypoint_rows()
    gc = gspread.service_account('credentials2.json')
    worksheet = gc.open_by_key('1SASg6rYtYl2TeVTvBCNOnW6IyzbBjSlzolsEil9JPZQ').sheet1
    for n in range(1+len(tour)//n_waypoints):
        create_waypoint_text(tour[n*n_waypoints:(n+1)*n_waypoints], first_waypoint_rows)
        if n!=len(tour)//n_waypoints:
            input(f'\nHit enter when you want to display the next set of waypoints')
        else:
            input(f'\nCongrats! This is your last set of waypoints. Hit enter to mark them as raided and remove them from your waypoint file')
        first_waypoint_rows = get_first_waypoint_rows() # this runs each loop so that if the user adds more waypoints during the loop, they are not removed at the end of the loop
        print('Updating server spreadsheet with raided cities')
        batch_data = []
        for city_index in tour[n*n_waypoints:(n+1)*n_waypoints]:
            x, z = city_list[city_index]
            raided_city_index = -1
            for i in original_indexes:
                if unraided_cities_x[i] == x and unraided_cities_z[i] == z:
                    raided_city_index = i
            if raided_city_index == -1:
                print(f'WARNING: No cities in the original_indexes of unraided_cities match the city we are looking for with {x = } and {z = }')
            row_number = unraided_cities_row_indexes[raided_city_index]
            batch_data.append({'range': f'C{row_number}', 'values': [['raided']]})
        worksheet.batch_update(batch_data)
        print(f'Marked {len(tour[n*n_waypoints:(n+1)*n_waypoints])} cities as raided')
    with open(waypoint_file, "r+") as f: # this removes the last set of end city waypoints from the waypoint file
        for row in first_waypoint_rows:
            f.writelines("".join(row) + "\n")

def get_first_waypoint_rows():
    # first_waypoint_rows = ['#','#waypoint:name:initials:x:y:z:color:disabled:type:set:rotate_on_tp:tp_yaw:visibility_type:destination','#']
    first_waypoint_rows = []
    with open(waypoint_file, "r") as f:
        reader = csv.reader(f)
        first_line = next(reader)[0]
        if first_line == '#': # the only set in the waypoint file is the default set, so we're going to make a sets list and add EndRaidingSoftware to the front of the list so it shows up when you log in
            first_waypoint_rows.append('sets:EndRaidingSoftware:gui.xaero_default')
            first_waypoint_rows.append('#')
        else: # if there is more than one waypoint set already, make EndRaidingSoftware be the first set in the list
            first_waypoint_rows.append(f'sets:EndRaidingSoftware{str(first_line[4:]).replace(":EndRaidingSoftware", "")}')
        for row in reader:
            if 'EndRaidingSoftware' not in str(row):
                first_waypoint_rows.append(row[0])
    return first_waypoint_rows

def create_waypoint_text(next_tour_points, first_waypoint_rows): # this adds the waypoints to your Minecraft instance
    colors = [4,12,6,14,10,2,11,3,9,1,13,5,0,8,7,15]
    waypoint_rows = first_waypoint_rows.copy()
    for n in range(len(next_tour_points)):
        x, z = city_list[next_tour_points[n]]
        waypoint_rows.append(f'waypoint:{n+1}:{n+1}:{x}:130:{z}:{colors[n]}:false:0:EndRaidingSoftware:false:0:0:false') # This adds the waypoints to a new waypoint set named EndRaidingSoftware
    with open(waypoint_file, "r+") as f:
        for row in waypoint_rows:
            f.writelines("".join(row) + "\n")

if __name__ == "__main__":
    main()
