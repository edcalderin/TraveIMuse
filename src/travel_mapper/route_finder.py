import logging
import os
import time
from datetime import datetime

import googlemaps
import numpy as np
from dotenv import load_dotenv
from googlemaps.convert import decode_polyline

from src.agents.locations import Trip
from src.travel_mapper.route_mapper import RouteMapper

load_dotenv()
print(os.getenv("GOOGLE_MAPS_API_KEY"))


class RouteFinder:
    MAX_WAYPOINTS_API_CALL: int = 25

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.INFO)
        self.mapper = RouteMapper()
        self.gmaps = googlemaps.Client(key=os.getenv("GOOGLE_MAPS_API_KEY"))

    def generate_route(self, list_of_places, itinerary, include_map=True):
        self.logger.info("# " * 20)
        self.logger.info("PROPOSED ITINERARY")
        self.logger.info("# " * 20)
        self.logger.info(itinerary)

        t1 = time.time()
        directions, sampled_route, mapping_dict = self.build_route_segments(
            list_of_places
        )
        t2 = time.time()
        self.logger.info(f"Time to build route : {round(t2 - t1, 2)}")

        if include_map:
            t1 = time.time()
            self.mapper.add_list_of_places(list_of_places)
            self.mapper.generate_route_map(directions, sampled_route)
            t2 = time.time()
            self.logger.info(f"Time to generate map : {round(t2 - t1, 2)}")

        return directions, sampled_route, mapping_dict

    def convert_to_coords(self, input_address):
        return self.gmaps.geocode(input_address)

    def build_route_segments(
        self, list_of_places: Trip, verbose=True, distance_per_point_in_km=0.25
    ):
        number_of_stops = len(list_of_places.waypoints)

        segment_mapping_dicts = []
        directions_list = []
        routes_list = []
        sampled_routes = []

        # if this is true, we need to make several API calls to collect the entire route
        if number_of_stops > self.MAX_WAYPOINTS_API_CALL:
            self.logger.info(
                f"""Number of stops ({number_of_stops}) > MAX_WAYPOINTS_PER_CALL
                ({self.MAX_WAYPOINTS_API_CALL}), going to make several calls to Google
                Maps API"""
            )
            starting_point = list_of_places.start
            for segment_id, segment_start in enumerate(
                range(0, number_of_stops, self.MAX_WAYPOINTS_API_CALL)
            ):
                segment_end = segment_start + self.MAX_WAYPOINTS_API_CALL

                segment_waypoints = list_of_places.waypoints[segment_start:segment_end]

                if segment_end >= number_of_stops:
                    # this is the final segment
                    end_point = list_of_places.end
                else:
                    end_point = segment_waypoints[-1]

                start_point = starting_point

                mapping_dict = self.build_mapping_dict(
                    start_point, end_point, waypoints=segment_waypoints[:-1]
                )

                if verbose:
                    self.logger.info("# " * 10)
                    self.logger.info(f"Getting directions for segment {segment_id}")

                directions, route = self.build_directions_and_route(
                    mapping_dict, verbose=verbose
                )
                sampled_route = self.sample_route_with_legs(
                    route, distance_per_point_in_km
                )

                directions_list += directions
                routes_list += route
                sampled_routes.append(sampled_route)

                segment_mapping_dicts.append(mapping_dict)

                starting_point = end_point
                segment_id += 1

            # combine and assemble as single mapping dict and route list from the
            # segments
            mapping_dict, sampled_route = self.assemble_final_route_from_segments(
                segment_mapping_dicts, sampled_routes
            )
            directions = directions_list

        # if we can just do one API call to Google Maps, then the process is simpler
        else:
            self.logger.info("Assembling mapping dictionary")
            mapping_dict = self.build_mapping_dict(
                list_of_places.start,
                list_of_places.end,
                waypoints=list_of_places.waypoints,
            )

            self.logger.info("Calling Google Maps API to get directions")
            directions, route = self.build_directions_and_route(mapping_dict)
            sampled_route = self.sample_route_with_legs(route, distance_per_point_in_km)

        return directions, sampled_route, mapping_dict

    def build_mapping_dict(self, start, end, waypoints):
        """

        Parameters
        ----------
        start
        end
        waypoints

        Returns
        -------

        """
        mapping_dict = {}
        mapping_dict["start"] = self.convert_to_coords(start)[0]
        mapping_dict["end"] = self.convert_to_coords(end)[0]

        if waypoints:
            for i, waypoint in enumerate(waypoints):
                mapping_dict[f"waypoint_{i}"] = self.convert_to_coords(waypoint)[0]

        return mapping_dict

    @staticmethod
    def get_route(directions_result):
        """

        Parameters
        ----------
        directions_result

        Returns
        -------

        """
        waypoints = {}

        for leg_number, leg in enumerate(directions_result[0]["legs"]):
            leg_route = {}

            distance, duration = leg["distance"]["text"], leg["duration"]["text"]
            leg_route["distance"] = distance
            leg_route["duration"] = duration
            leg_route_points = []

            for step in leg["steps"]:
                decoded_points = decode_polyline(step["polyline"]["points"])
                for p in decoded_points:
                    leg_route_points.append(f"{p['lat']},{p['lng']}")

            leg_route["route"] = leg_route_points
            waypoints[leg_number] = leg_route

        return waypoints

    def build_directions_and_route(
        self, mapping_dict, start_time=None, transit_type=None, verbose=True
    ):
        if not start_time:
            start_time = datetime.now()

        if not transit_type:
            transit_type = "driving"

        # use of place_id makes the calls more efficient
        # see https://developers.google.com/maps/documentation/directions/get-directions#Waypoints
        waypoints = [
            "place_id:" + mapping_dict[x]["place_id"]
            for x in mapping_dict
            if "waypoint" in x
        ]
        start = "place_id:" + mapping_dict["start"]["place_id"]
        end = "place_id:" + mapping_dict["end"]["place_id"]

        # waypoints = [
        #     mapping_dict[x]["place_id"]
        #     for x in mapping_dict.keys()
        #     if "waypoint" in x
        # ]
        # start = mapping_dict["start"]["formatted_address"]
        # end = mapping_dict["end"]["formatted_address"]

        directions_result = self.gmaps.directions(
            start,
            end,
            waypoints=waypoints,
            mode=transit_type,
            units="metric",
            optimize_waypoints=True,
            traffic_model="best_guess",
            departure_time=start_time,
        )

        # test
        # directions_result = []

        if directions_result:
            full_route = self.get_route(directions_result)

        else:
            # if we get here, the google maps call has failed. This is probably because
            # the waypoints were not found. We can still make a map by just using the
            # start and end locations but we need to warn the user that the map won't
            # contain the waypoints

            self.logger.warning(
                f"WARNING, some of the waypoints {waypoints} seem to"
                "have caused issues with the google maps api"
            )

            self.logger.warning(
                "Will attempt to step through the directions point by point"
            )

            all_points = [start] + waypoints + [end]
            start_time = datetime.now()
            final_route_dict = {}
            directions_list = []
            for i in range(1, len(all_points)):
                # iterate edge by edge and get the directions between
                # the points. For some reason this seems better able to
                # deal with remote waypoints than if we enter "waypoints"
                # into the directions call
                p1 = all_points[i]
                p0 = all_points[i - 1]

                directions_result = self.gmaps.directions(
                    p0,
                    p1,
                    units="metric",
                    mode=transit_type,
                    departure_time=start_time,
                )
                if directions_result:
                    route_dict = self.get_route(directions_result)
                    final_route_dict[i - 1] = route_dict[0]
                directions_list += directions_result

            directions_result = directions_list
            full_route = final_route_dict

        if verbose:
            print("# " * 10)
            print("Fetched directions")
            print("# " * 10)

            if len(directions_result) == 1:
                # print out some stats for the legs of the proposed trip
                for i, leg in enumerate(directions_result[0]["legs"]):
                    print(
                        "Stop:" + str(i),
                        leg["start_address"],
                        "==> ",
                        leg["end_address"],
                        "distance (km): ",
                        leg["distance"]["value"] / 1000,
                        "traveling Time (hrs): ",
                        leg["duration"]["value"] / 3600,
                    )
            else:
                # if the directions result has been built from multiple calls
                for i, leg in enumerate(directions_result):
                    leg = leg["legs"][0]
                    print(
                        "Stop:" + str(i),
                        leg["start_address"],
                        "==> ",
                        leg["end_address"],
                        "distance (km): ",
                        leg["distance"]["value"] / 1000,
                        "traveling Time (hrs): ",
                        leg["duration"]["value"] / 3600,
                    )

        return directions_result, full_route

    @staticmethod
    def assemble_final_route_from_segments(segment_mapping_dicts, sampled_routes):
        final_mapping_dict = {}
        final_sampled_route = {}

        final_segment_id = len(segment_mapping_dicts) - 1
        waypoint_count = 0
        sampled_waypoint_count = 0

        for i, segment in enumerate(segment_mapping_dicts):
            # at the start of the route, get the start of the segment
            if i == 0:
                final_mapping_dict["start"] = segment["start"]
            # at the end of the route, get the final point
            elif i == final_segment_id:
                final_mapping_dict["end"] = segment["end"]

            # add all the waypoints in the correct order
            for _k, _ in segment.items():
                if "waypoint_" in _k:
                    final_mapping_dict[f"waypoint_{waypoint_count}"] = segment[_k]
                    waypoint_count += 1

            sampled_route = sampled_routes[i]
            for _, v in sampled_route.items():
                final_sampled_route[sampled_waypoint_count] = v
                sampled_waypoint_count += 1

        return final_mapping_dict, final_sampled_route

    @staticmethod
    def sample_route_with_legs(route, distance_per_point_in_km=0.25):
        """

        Parameters
        ----------
        route
        npoints

        Returns
        -------

        """
        # get total distance
        all_distances = sum(
            [float(route[i]["distance"].split(" ")[0].replace(",", "")) for i in route]
        )

        # find distance per point
        npoints = int(np.ceil(all_distances / distance_per_point_in_km))

        # get actual points per leg
        points_per_leg = [len(v["route"]) for k, v in route.items()]
        total_points = sum(points_per_leg)

        # get fraction of total points that need to be represented on each leg
        n_sampled_per_leg = [
            max(1, np.round(npoints * (x / total_points), 0)) for x in points_per_leg
        ]

        sampled_points = {}
        for leg_id, route_info in route.items():
            total_points = int(points_per_leg[leg_id])
            total_sampled_points = int(n_sampled_per_leg[leg_id])
            step_size = int(max(total_points // total_sampled_points, 1.0))
            route_sampled = [
                route_info["route"][idx] for idx in range(0, total_points, step_size)
            ]

            distance = route_info["distance"]
            duration = route_info["duration"]

            sampled_points[leg_id] = {
                "route": [
                    (float(x.split(",")[0]), float(x.split(",")[1]))
                    for x in route_sampled
                ],
                "duration": duration,
                "distance": distance,
            }

        return sampled_points
