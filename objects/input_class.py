import pandas as pd
import numpy as np
import random as rnd
import networkx as nx

class Inputs():
    def __init__(self,num_points = None):
        self.points = num_points

    def random_point_generator(self,num_points):
        """
        Generate random latitude and longitude points from a given center (just to simulate ;) )

        Params
        --------------
        num_points : int (how much data you want)

        Returns
        ------------
        latitude: latitude random points
        longitude: longtiude random points
        """

        origin_point = (-12.0432,-77.0141)
        latitude = []
        longitude = []
        for row in range(num_points):
            temp = float(rnd.randint(0,100))
            latitude.append(origin_point[0] + rnd.random()/100)
            longitude.append(origin_point[1] + rnd.random()/100)
        return latitude,longitude


    def generate_demand(self,num_points):
        """
        Generate random daily demands given the needed distribution points

        Params
        --------------
        num_points : int (how much data you want)

        Returns
        ------------
        df : DataFrame with latitude,longitude of points as well as demand for the
             vending machines

        """

        latitude,longitude = self.random_point_generator(num_points)
        demand = np.array([np.random.randint(10,100) for observation in range(num_points)])


        return latitude, longitude, demand

    def cost_matrix(self,num_points):
        """
        Creates a cost matrix for the model to later minimize (cost function must be defined first).
        For now just return the distance between the points. FUTURE : Use Google API (optimized performance, but costs).
        For now using osmnx algorithm for calculating shortest paths from a graph (dijkstra algorithm)

        Params
        --------------
        num_points : int (how much data you want)

        Returns
        ------------

        """
        latitude,longitude,demand = self.generate_demand(num_points)
        lat_lon = tuple(zip(latitude,longitude))
        g = ox.graph_from_point((-12.0432,-77.0141) , distance = 500)
        matrix = np.zeros((num_points,num_points))
        for row in range(num_points):
            temp1 = ox.get_nearest_node(g,lat_lon[row])
            for column in range(num_points):
                temp2 = ox.get_nearest_node(g,lat_lon[column])
                distance = nx.shortest_path_length(g,source = temp1,target = temp2)
                matrix[row,column] = distance
        return matrix, lat_lon, demand

    def prediccion(self,date,df):
        from datetime import timedelta
        from datetime import datetime
        pred_date = datetime.strptime(date,"%Y-%m-%d") + timedelta(days = 1)
        print(pred_date)
        predicciones = []
        names = []
        lat = []
        lon = []
        df = df[df.date<date]
        for name in np.array(df.Name.unique()):
            caso = df[df.Name == name]
            pred = np.sum(caso.current_count[-7:-1])/6
            names.append(name)
            predicciones.append(np.round(pred))

        pred_df = pd.DataFrame({'name':names,'prediction':np.array(predicciones)/100})
        pred_df['prediction_date'] = pred_date
        return pred_df
