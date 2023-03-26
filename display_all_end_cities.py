import gspread # from https://github.com/burnash/gspread
from matplotlib import pyplot as plt
from matplotlib.lines import Line2D
from mpl_interactions import panhandler, zoom_factory # from https://mpl-interactions.readthedocs.io/en/stable/examples/zoom-factory.html
from time import sleep

waypoint_file = 'C:\Users\Matthew\curseforge\minecraft\Instances\Xareos Minimap and Worldmap\XaeroWaypoints\Multiplayer_mogswamp.apexmc.co\dim%1\mw$default_1.txt'

def main():
    global worksheet, gc, all_cities_x,all_cities_y, n_cities
    n_cities = int(input('How many cities would you like to end raid? '))
    print('Getting coordinates from server spreadsheet')
    gc = gspread.service_account('credentials2.json')
    worksheet = gc.open_by_key('1SASg6rYtYl2TeVTvBCNOnW6IyzbBjSlzolsEil9JPZQ').sheet1
    print(f'worksheet = {worksheet}')
    all_cities_x = list(map(int, worksheet.col_values(1)[1:])) # Get all values from the first column
    all_cities_y = list(map(int, worksheet.col_values(2)[1:])) # Get all values from the second column
    print('Click on the first end city you would like to raid')
    start_canvas1()

def start_canvas1():
    global fig, ax, ax2background, points
    plt.ioff()
    fig, ax = plt.subplots(1, 1, figsize=((6.5,6)))
    fig.canvas.mpl_connect('pick_event', onpick) # necessary
    ax.set_aspect('equal')
    plt.xlabel("X-axis")
    plt.ylabel("Y-axis")
    max_x, min_x,  max_y, min_y = 25000, -25000,  25000, -25000
    # city_x, city_y = closest_cities(max_x, min_x, max_y, min_y)
    city_x1, city_y1 = all_cities_x, all_cities_y
    # points, = ax.scatter(city_x, city_y, [7 for _ in range(len(city_x))], [[0,0,0] for _ in range(len(city_x))], picker=True)
    points1 = ax.scatter(city_x1, city_y1, [7 for _ in range(len(city_x1))], [[0,0,0] for _ in range(len(city_x1))], picker=True)
    # points = ax.plot(city_x, city_y, 'k.')
    points, = ax.plot([])
    # ax.plot(city_x, city_y, picker=True)
    # max_x, min_x,  max_y, min_y =  max(city_x)/5, min(city_x)/5, max(city_y)/5, min(city_y)/5
    # width = max_x - min_x
    # height = max_y - min_y
    ax.set(xlim=(min_x, max_x), ylim=(min_y, max_y))
    fig.canvas.draw()
    fig.canvas.manager.window.wm_geometry("+%d+%d" % (0, 0)) # move figure to top right of screen
    ax2background = fig.canvas.copy_from_bbox(ax.bbox)
    # fig.canvas.blit(ax.bbox)
    # fig.canvas.flush_events()
    # fig.canvas.resize_event()
    # plt.show(block=False)
    disconnect_zoom = zoom_factory(ax)
    pan_handler = panhandler(fig)
    plt.show()
    # draw_tour()

# def draw_tour():
#     while True:
#         fig.canvas.restore_region(ax2background)
#         max_x, min_x = ax.get_xlim()
#         max_y, min_y = ax.get_ylim()
#         city_x, city_y = closest_cities(max_x, min_x, max_y, min_y)
#         points.set_data(city_x, city_y)
#         ax.draw_artist(points)
#         fig.canvas.blit(ax.bbox)
#         fig.canvas.flush_events()
#         fig.canvas.resize_event()
#         print('hi')

def onpick(event):
    global all_cities_x, all_cities_y
    if event.mouseevent.button == 1:
        ind = event.ind
        # print(f'ind = {ind}')
        first_city_x, first_city_y = all_cities_x[ind[0]], all_cities_y[ind[0]]
        print(f'You have picked your first city to be at {all_cities_x[ind[0]], all_cities_y[ind[0]]}')
        path = get_a_path(first_city_x, first_city_y)

def closest_cities(max_x, min_x, max_y, min_y, cities_x, cities_y):
    # global city_x, city_y, city_list
    city_x = []
    city_y = []
    city_list = []
    for n in range(len(cities_x)):
        if min_x < cities_x[n] < max_x and min_y < cities_y[n] < max_y:
            x = int(cities_x[n])
            y = int(cities_y[n])
            city_x.append(x)
            city_y.append(y)
            city_list.append([x, y])
    return city_x, city_y, city_list

def get_a_path(first_city_x, first_city_y):
    plt.close()
    # n_cities = int(input('How many cities would you like to end raid? '))
    limit = 2000 * n_cities ** 0.5 + 80 * n_cities
    max_x, min_x, max_y, min_y = first_city_x + limit, first_city_x - limit, first_city_y + limit, first_city_y - limit
    global city_x, city_y, city_list
    incrase = 1.2 # increases the cities around the border of the selected path which can be selected later on
    city_x, city_y, city_list = closest_cities(1.2*max_x, 1.2*min_x, 1.2*max_y, 1.2*min_y, all_cities_x, all_cities_y)
    start_canvas()
    city_indexes = get_city_indexes()
    # global city_x, city_y, city_list
    list, city_list = limited_nn_algorithm(city_list.index([first_city_x, first_city_y]), city_indexes.copy(), n_cities)
    city_x, city_y = [c[0] for c in city_list], [c[1] for c in city_list]
    city_list = [[city_x[n], city_y[n]] for n in range(len(city_x))]
    # print(f'list = {list}')
    make_distance_array()
    original_distance = find_total_distance(list)
    plt.close()
    start_canvas()
    tour, what = use_all_methods(list, original_distance, 1, original_distance, len(list))
    print(f'city_coordinates = ({[city_list[city] for city in tour]}')
    # print(f'closest_cities_x = {city_x}')
    # print(f'closest_cities_y = {city_y}')
    # print(f'{[city_list[c][0] for c in tour]}')
    # print(f'{[x for x in city_x]}')
    print(f'closest_cities_x = {[x for x in city_x if x not in (city_list[c][0] for c in tour)]}')
    print(f'closest_cities_y = {[y for y in city_y if y not in (city_list[c][1] for c in tour)]}')
    update_waypoints(tour)
    plt.close()

def update_waypoints(tour): # this functions updates the waypoints as users tell the program that they have visited the cities
    n_waypoints = 12 # this is the default number of cities to display all at once because it's the most colors you can have in a rainbow sequence
    for n in range(len(tour)//n_waypoints):
        create_waypoint_text(n_waypoints, tour[n*n_waypoints:(n+1)*n_waypoints]) # ths will probably need to be adjusted layer for the lst bath of points in a tour, which might not be divisible by 12

def create_waypoint_text(number, next_tour_points):
    colors = [4,12,6,14,10,2,11,3,9,1,13,5,0,8,7,15]
    waypoint_text_lines = ['#','#waypoint:name:initials:x:y:z:color:disabled:type:set:rotate_on_tp:tp_yaw:visibility_type:destination','#']
    for n in range(len(number)):
        x, y = city_list[next_tour_points[n]]
        waypoint_text_lines.append(f'waypoint:{n}:{n}:{x}:{y}:200:{colors[n]}:false:0:gui.xaero_default:false:0:0:false')
    with open(waypoint_file, "r+") as f:
        for text_line in waypoint_text_lines:
            f.writelines(text_line)
            f.writelines("\n")

def limited_nn_algorithm(first_city, city_indexes, n_cities):
    beeline_list = [first_city]
    city_indexes.remove(first_city)
    fig.suptitle(f'Nearest Neighbor Algorithm')
    fig.canvas.resize_event()
    fig.canvas.flush_events()
    draw_nearest_neighbor([])
    last_city = first_city
    for _ in range(n_cities):
        nearest_city = find_nearest_neighbor(last_city, city_indexes)
        beeline_list.append(nearest_city)
        city_indexes.remove(nearest_city)
        last_city = nearest_city
        draw_nearest_neighbor(beeline_list)
    return list(range(len(beeline_list))), [city_list[b] for b in beeline_list]

def find_nearest_neighbor(city_1, city_indexes):
    indexes_copy = city_indexes.copy()
    if city_1 in indexes_copy:
        indexes_copy.remove(city_1)
    distances = make_relative_distance_lists(indexes_copy, city_1)
    distances.sort()
    indexes_copy = city_indexes
    return distances[0][1]

def make_relative_distance_lists(city_indexes, city_1):
    distances = []
    '''distances = [[x_coord, y_coord], distance]'''
    for city_2 in city_indexes:
        x = city_list[city_2][0] - city_list[city_1][0]
        y = city_list[city_2][1] - city_list[city_1][1]
        distances.append([x * x + y * y, city_2])
    return distances

def use_all_methods(shortest_points, old_shortest_distance, number, original_distance, number_of_points):
    ordinal = ['0th','1st','2nd','3rd','4th','5th','6th','7th','8th','9th','10th','11th','12th']
    loop_number = 1
    n_changes, n_changes_1, n_changes_2, n_changes_3 = 0, 0, 0, 0
    while True:
        print(f'\nStarting Switchblade Algorithim for the {ordinal[loop_number]} time')
        update_title(find_total_distance(shortest_points), original_distance, 'Flip Segments')
        shortest_points, old_shortest_distance, n_changes_1 = switchblade(shortest_points, number_of_points, old_shortest_distance, original_distance, number)
        if n_changes_1 + n_changes_3 != 0:
            print(f'\nStarting Rearrange Algorithim for the {ordinal[loop_number]} time')
            update_title(find_total_distance(shortest_points), original_distance, 'Rearrange Points')
            shortest_points, old_shortest_distance, n_changes_2 = rearrange_points(shortest_points, number_of_points, old_shortest_distance, original_distance, number)
        else:
            n_changes_2 = 0
        if n_changes_1 + n_changes_2 != 0:
            print(f'\nStarting Shift Sections Algorithim for the {ordinal[loop_number]} time')
            update_title(find_total_distance(shortest_points), original_distance, 'Shift Section')
            shortest_points, old_shortest_distance, n_changes_3 = shift_sections(shortest_points, number_of_points, old_shortest_distance, original_distance, number)
        else:
            n_changes_3 = 0
        n_changes += n_changes_1 + n_changes_2 + n_changes_3
        loop_number += 1
        if n_changes_1 + n_changes_2 + n_changes_3 == 0:
            print('Path optimization complete')
            return shortest_points, n_changes

def make_distance_array():
    global distance_array
    distance_array = []
    for city_1 in city_list:
        distance_list = []
        for city_2 in city_list:
            x = (city_1[0]-city_2[0])
            y = (city_1[1]-city_2[1])
            distance_list.append((x * x + y * y) ** 0.5)
        distance_array.append(distance_list)

def move_list(points, i, s, n): # i = list_start_index, s = list_length, n = This is the index where the list is being moved to
    points_copy = points.copy()
    move_list = []
    for c in range(s):
        move_list.append(points[i+c])
    for c in range(s):
        points_copy.remove(points[i+c])
    if i < n:
        for c in range(s):
            points_copy.insert(n-s+c, move_list[c])
    elif n < i:
        for c in range(s):
            points_copy.insert(n+c, move_list[c])
    else:
        print('invalid move')
    return points_copy, move_list

def shift_sections(points, number_of_points, old_shortest_distance, original_distance, number):
    f = len(points) - 1 # the index of the last point in the list
    for s in range(2, 13): # the number of points being moved
        for i in range(len(points)-1-s): # the index of the start of the points being moved
            for n in range(0, f+1): # the index of the place the points are being moved to
                if n not in range(i, i+s+2):
                    if 0 < i and i+s-1 < f and 0 < n < f+1:
                        if i < n:
                            old_distance = distance(points[i-1],points[i]) + distance(points[i+s-1],points[i+s]) + distance(points[n-1],points[n])
                            new_distance = distance(points[i-1],points[i+s]) + distance(points[n-1],points[i]) + distance(points[i+s-1],points[n])
                        elif n < i:
                            old_distance = distance(points[n-1],points[n]) + distance(points[i-1],points[i]) + distance(points[i+s-1],points[i+s])
                            new_distance = distance(points[n-1],points[i]) + distance(points[i+s-1],points[n]) + distance(points[i-1],points[i+s])
                    elif i == 0:
                        if n == f+1:
                            old_distance = distance(points[i+s-1],points[i+s])
                            new_distance = distance(points[n-1],points[i])
                        else:
                            old_distance = distance(points[i+s-1],points[i+s]) + distance(points[n-1],points[n])
                            new_distance = distance(points[n-1],points[i]) + distance(points[i+s-1],points[n])
                    elif i+s-1 == f:
                        if n == 0:
                            old_distance = distance(points[i-1],points[i])
                            new_distance = distance(points[i+s-1],points[n])
                        else:
                            old_distance = distance(points[n-1],points[n]) + distance(points[i-1],points[i])
                            new_distance = distance(points[n-1],points[i]) + distance(points[i+s-1],points[n])
                    elif i+s-1 < f and n == 0:
                        old_distance = distance(points[i-1],points[i]) + distance(points[i+s-1],points[i+s])
                        new_distance = distance(points[i+s-1],points[n]) + distance(points[i-1],points[i+s])
                    elif 0 < i and n == f+1:
                        old_distance = distance(points[i-1],points[i]) + distance(points[i+s-1],points[i+s])
                        new_distance = distance(points[i-1],points[i+s]) + distance(points[n-1],points[i])
                    else:
                        print(f'There has been a serious error!')
                        print(f'i = {i}, s = {s},  n = {n}')
                    distance_saved = old_distance - new_distance
                    if 0 < distance_saved:
                        shifted_points, moved_list = move_list(points.copy(), i, s, n)
                        is_shorter, new_shortest_distance, number = report_progress('Shift Section', shifted_points, number, original_distance, number_of_points, old_shortest_distance, i, n, distance_saved)
                        if is_shorter:
                            if i == 0 and n < f and s != f:
                                draw_tour(new_shortest_distance, original_distance, 'Shift Section', shifted_points, [points[n-1], moved_list[0]], [moved_list[-1], points[n]], [])
                            elif s == f or n == 0 or n == f+1:
                                pass
                            else:
                                draw_tour(new_shortest_distance, original_distance, 'Shift Section', shifted_points, [points[n-1], moved_list[0]], [moved_list[-1], points[n]], [points[i-1], points[i+s]])
                            global fig
                            update_title(new_shortest_distance, original_distance, 'Flip Segments')
                            shifted_points, old_shortest_distance, ignore = switchblade(shifted_points, number_of_points, new_shortest_distance, original_distance, number)
                            update_title(new_shortest_distance, original_distance, 'Shift Section')
                            return shift_sections(shifted_points, number_of_points, new_shortest_distance, original_distance, number)
                        else:
                            print(f'i = {i}, s = {s},  n = {n}')
    return points, old_shortest_distance, number

def reverse_list(points, shortest_distance, reverse_start_index, reverse_end_index):
    points_copy = points.copy()
    reverse_list = []
    list_length = reverse_end_index - reverse_start_index
    for i in range(list_length):
        reverse_list.append(points[reverse_start_index+i])
        points_copy.remove(points[reverse_start_index+i])
    for n in range(list_length):
        points_copy.insert(reverse_start_index, reverse_list[n])
    total_distance = find_total_distance(points_copy)
    if total_distance > shortest_distance:
        return points_copy
    else:
        print('someting went wrong with reversing the list')
        print(f'total_distance = {total_distance}')
        print(f'shortest_distance = {shortest_distance}')

def switchblade(points, number_of_points, old_shortest_distance, original_distance, number):
    for i in range(len(points)-1):
        for n in range(i+1,len(points)):
            if i > 0:
                old_distance = distance(points[i-1],points[i]) + distance(points[n-1],points[n])
                new_distance = distance(points[i],points[n]) + distance(points[i-1],points[n-1])
            elif i == 0:
                old_distance = distance(points[n-1],points[n])
                new_distance = distance(points[i],points[n])
            else:
                print(f'\n\n\nSorry, there has been an error!!')
            distance_saved = old_distance - new_distance
            if 0 < distance_saved:
                switched_points = reverse_list(points.copy(), new_distance, i, n)
                is_shorter, new_shortest_distance, number = report_progress('Switchblade', switched_points, number, original_distance, number_of_points, old_shortest_distance, i, n, distance_saved)
                if is_shorter:
                    if i == 0:
                        draw_tour(new_shortest_distance, original_distance, 'Flip Segments', switched_points, [points[i], points[n]], [], [])
                    elif i < n:
                        draw_tour(new_shortest_distance, original_distance, 'Flip Segments', switched_points, [points[i], points[n]], [points[i-1],points[n-1]], [])
                    return switchblade(switched_points, number_of_points, new_shortest_distance, original_distance, number)
    return points, old_shortest_distance, number - 1

def report_progress(name, switched_points, number, original_distance, number_of_points, old_shortest_distance, i, n, distance_saved):
    new_shortest_distance = find_total_distance(switched_points) # Remove this line when you feel that the code is ready
    if len(switched_points) != number_of_points:
        print('There has been an error. A point has been lost')
        print(f'len(switched_points) = {len(switched_points)},   number_of_points = {number_of_points}')
        return False, old_shortest_distance, number
    if round(new_shortest_distance,7) != round(old_shortest_distance - distance_saved,7):
        print('There was an error. the change in distance was not what we expected it to be.')
        # print(f'old_shortest_distance = {old_shortest_distance}')
        # print(f'new_shortest_distance = {new_shortest_distance}')
        # print(f'find_total_distance(switched_points) = {find_total_distance(switched_points)}')
        # print(f'old_shortest_distance - distance_saved = {old_shortest_distance - distance_saved}')
        # print(f'distance_saved = {distance_saved}')
        print(f'{new_shortest_distance} != {old_shortest_distance - distance_saved}')
    if new_shortest_distance < old_shortest_distance:
        # print(f'\n{name} Optimization number {number}:')
        print(f'Congrats! We found a new shorter path with a distance of {new_shortest_distance}')
        # print(f'This optimization makes it {(old_shortest_distance - new_shortest_distance):.4f} shorter than the last path!')
        # print(f'The path is now {100*(1 - new_shortest_distance/original_distance):.4f}% shorter than the original path!')
        # print(f'The path is now {(original_distance - new_shortest_distance):.4f} shorter than the original path!')
        number += 1
        return True, new_shortest_distance, number
    else:
        print(f'\n\n\nAn error has occurred! The line we calculated was shorter was not really shorter!')
        print(f'i = {i}, n = {n}')
        print(f'distance_saved = {distance_saved}')
        print(f'old_shortest_distance = {old_shortest_distance}.  new_shortest_distance = {new_shortest_distance}')
        return False, old_shortest_distance, number - 1

def rounded(number, decimals=0):
    multiplier = 10 ** decimals
    return round(number * multiplier) / multiplier

def distance(city_1,city_2):
    return distance_array[city_1][city_2]

def find_total_distance(list): #This is meant for lists of points only
    total_distance = 0
    for n in range(len(list)-1):
        dist = distance(list[n],list[n+1])
        total_distance += dist
    return total_distance

def extract_points(list):
    list_x = [city_list[city][0] for city in list]
    list_y = [city_list[city][1] for city in list]
    # for city in list:
    #     point = city_list[city]
    #     list_x.append(point[0])
    #     list_y.append(point[1])
    return list_x, list_y

def get_city_indexes():
    return list(range(len(city_list)))

def update_title(new_shortest_distance, original_distance, algorithm_name):
    fig.suptitle(f'Distance = {new_shortest_distance:.3f}, Improvement = {(100*(original_distance - new_shortest_distance)/original_distance):.2f}%\nCurrent Algorithm: {algorithm_name}')
    fig.canvas.resize_event()
    fig.canvas.flush_events()

def draw_nearest_neighbor(tour):
    # global fig, ax, line1, ax2background
    line1.set_data(extract_points(tour))
    fig.canvas.restore_region(ax2background)
    ax.draw_artist(line1)
    fig.canvas.blit(ax.bbox)
    fig.canvas.flush_events()

def draw_tour(new_shortest_distance, original_distance, algorithm_name, blue_line, first_red_segment, second_red_segment = None, third_red_segment = None):
    # global fig, ax, line1, line2, line3, line4, ax2background
    fig.canvas.restore_region(ax2background)
    line1.set_data(extract_points(blue_line))
    ax.draw_artist(line1)
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
    fig.suptitle(f'Distance = {new_shortest_distance:.3f}, Improvement = {(100*(original_distance - new_shortest_distance)/original_distance):.2f}%\nCurrent Algorithm: {algorithm_name}')
    fig.canvas.blit(ax.bbox)
    fig.canvas.flush_events()
    fig.canvas.resize_event()

def start_canvas():
    global fig, ax, line1, line2, line3, line4, ax2background
    fig, ax = plt.subplots(1, 1, figsize=((6.5,6)))
    ax.set_aspect('equal')
    plt.xlabel("X-axis")
    plt.ylabel("Y-axis")
    city_x, city_y = extract_points(get_city_indexes())
    line1, = ax.plot([])
    line2, = ax.plot([])
    line3, = ax.plot([])
    line4, = ax.plot([])
    max_x, min_x,  max_y, min_y =  max(city_x), min(city_x), max(city_y), min(city_y)
    o_city_x, o_city_y, o_cities = closest_cities(max_x, min_x, max_y, min_y, all_cities_x, all_cities_y)
    ax.plot(o_city_x, o_city_y, 'y.')
    ax.plot(city_x, city_y, 'k.')
    width = max_x - min_x
    height = max_y - min_y
    ax.set(xlim=(min_x - width*0.05, max_x + width*0.05,), ylim=(min_y - height*0.05, max_y + height*0.05))
    fig.canvas.draw()
    move_figure(fig, 0, 0)
    ax2background = fig.canvas.copy_from_bbox(ax.bbox)
    plt.show(block=False)

def move_figure(f, x, y): # from https://stackoverflow.com/questions/7449585/how-do-you-set-the-absolute-position-of-figure-windows-with-matplotlib
    """Move figure's upper left corner to pixel (x, y)"""
    f.canvas.manager.window.wm_geometry("+%d+%d" % (x, y))

def rearrange_points(points, number_of_points, old_shortest_distance, original_distance, number):
    f = len(points) - 1 # index of final point
    for i in range(f+1): # index of the point that will be moved
        for n in range(f+1): # index where the point will be moved to
            if i != n:
                if 0 < i < f:
                    if i < n < f:
                        old_distance = distance(points[i-1],points[i]) + distance(points[i],points[i+1]) + distance(points[n],points[n+1])
                        new_distance = distance(points[i-1],points[i+1]) + distance(points[n],points[i]) + distance(points[i],points[n+1])
                    elif 0 < n < i:
                        old_distance = distance(points[i-1],points[i]) + distance(points[i],points[i+1]) + distance(points[n-1],points[n])
                        new_distance = distance(points[i-1],points[i+1]) + distance(points[n-1],points[i]) + distance(points[i],points[n])
                    elif n == f:
                        old_distance = distance(points[i-1],points[i]) + distance(points[i],points[i+1])
                        new_distance = distance(points[i-1],points[i+1]) + distance(points[n],points[i])
                    elif n == 0:
                        old_distance = distance(points[i-1],points[i]) + distance(points[i],points[i+1])
                        new_distance = distance(points[i],points[n]) + distance(points[i-1],points[i+1])
                elif i == 0:
                    if 0 < n < f:
                        old_distance = distance(points[i],points[i+1]) + distance(points[n],points[n+1])
                        new_distance = distance(points[n],points[i]) + distance(points[i],points[n+1])
                    elif n == f:
                        old_distance = distance(points[i],points[i+1])
                        new_distance = distance(points[n], points[i])
                elif i == f:
                    if n == 0:
                        old_distance = distance(points[i-1],points[i])
                        new_distance = distance(points[i],points[n])
                    elif 0 < n:
                        old_distance = distance(points[i-1],points[i]) + distance(points[n-1],points[n])
                        new_distance = distance(points[n-1],points[i]) + distance(points[i],points[n])
                else:
                    print("You're doing something wrong")
                    print(f' i = {i},  n = {n}')
                distance_saved = old_distance - new_distance
                if distance_saved > 0:
                    points_copy = points.copy()
                    points_copy.remove(points[i])
                    points_copy.insert(n, points[i])
                    is_shorter, new_shortest_distance, number = report_progress('Rearrange Points', points_copy, number, original_distance, number_of_points, old_shortest_distance, i, n, distance_saved)
                    if is_shorter and 0 < i < f and 0 < n < f:
                        draw_tour(new_shortest_distance, original_distance, 'Rearrange Points', points_copy, [points_copy[n-1], points_copy[n], points_copy[n+1]],[points[i-1], points[i+1]], [])
                    return rearrange_points(points_copy, number_of_points, new_shortest_distance, original_distance, number)
    return points, old_shortest_distance, number - 1

def reverse_path(points):
    reverse_list = []
    for point in points:
        reverse_list.insert(0,point)
    if round(find_total_distance(reverse_list),6) != round(find_total_distance(points),6):
        print('someting went wrong with reversing the list')
        print(f'find_total_distance(reverse_list) = {find_total_distance(reverse_list)}')
        print(f'find_total_distance(points) = {find_total_distance(points)}')
        0/0
    else:
        return reverse_list

def correct_starting_point(path):
    distance_to_start = distance([0,0],path[0])
    distance_to_end = distance([0,0],path[len(path)-1])
    if distance_to_start > distance_to_end:
        path = reverse_path(path)
        return path

if __name__ == "__main__":
    main()