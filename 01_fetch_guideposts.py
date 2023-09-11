import overpy
import os
import shutil
import helpers as myhelpers


def fetch_signposts(area_name):
    api = overpy.Overpass()
    query = f"""
    [out:json];
    area[name="{area_name}"]->.a;
    (
      node(area.a)["tourism"="information"];
      way(area.a)["tourism"="information"];
      relation(area.a)["tourism"="information"];
    );
    out center;
    """
    result = api.query(query)

    signposts = []

    for node in result.nodes:
        signposts.append((node.lat, node.lon, node.tags.get("information", "unknown"), node.tags.get("ref", "N/A")))

    for way in result.ways:
        signposts.append(
            (way.center_lat, way.center_lon, way.tags.get("information", "unknown"), way.tags.get("ref", "N/A")))

    for relation in result.relations:
        signposts.append((relation.center_lat, relation.center_lon, relation.tags.get("information", "unknown"),
                          relation.tags.get("ref", "N/A")))

    return signposts


def fetch_guideposts():
    area_names = [
        "Gemeinde Alberschwende",
        "Gemeinde Altach",
        "Gemeinde Andelsbuch",
        "Gemeinde Au",
        "Gemeinde Bartholomäberg",
        "Marktgemeinde Bezau",
        "Gemeinde Bildstein",
        "Gemeinde Bizau",
        "Gemeinde Blons",
        "Stadt Bludenz",
        "Gemeinde Bludesch",
        "Gemeinde Brand",
        "Stadt Bregenz",
        "Gemeinde Buch",
        "Gemeinde Bürs",
        "Gemeinde Bürserberg",
        "Gemeinde Dalaas",
        "Gemeinde Damüls",
        "Gemeinde Doren",
        "Stadt Dornbirn",
        "Gemeinde Düns",
        "Gemeinde Dünserberg",
        "Gemeinde Egg",
        "Gemeinde Eichenberg",
        "Stadt Feldkirch",
        "Gemeinde Fontanella",
        "Marktgemeinde Frastanz",
        "Gemeinde Fraxern",
        "Gemeinde Fußach",
        "Gemeinde Gaißau",
        "Gemeinde Gaschurn",
        "Gemeinde Göfis",
        "Götzis",
        "Marktgemeinde Hard",
        "Gemeinde Hittisau",
        "Gemeinde Höchst",
        "Marktgemeinde Hörbranz",
        "Stadt Hohenems",
        "Gemeinde Hohenweiler",
        "Gemeinde Innerbraz",
        "Gemeinde Kennelbach",
        "Gemeinde Klaus",
        "Gemeinde Klösterle",
        "Gemeinde Koblach",
        "Gemeinde Krumbach",
        "Gemeinde Langen bei Bregenz",
        "Gemeinde Langenegg",
        "Gemeinde Laterns",
        "Marktgemeinde Lauterach",
        "Gemeinde Lech",
        "Gemeinde Lingenau",
        "Gemeinde Lochau",
        "Gemeinde Lorüns",
        "Gemeinde Ludesch",
        "Marktgemeinde Lustenau",
        "Gemeinde Mäder",
        "Gemeinde Meiningen",
        "Gemeinde Mellau",
        "Gemeinde Mittelberg",
        "Gemeinde Möggers",
        "Marktgemeinde Nenzing",
        "Gemeinde Nüziders",
        "Gemeinde Raggal",
        "Marktgemeinde Rankweil",
        "Gemeinde Reuthe",
        "Gemeinde Riefensberg",
        "Gemeinde Röns",
        "Gemeinde Röthis",
        "Gemeinde Sankt Anton am Arlberg",
        "Gemeinde Sankt Gallenkirch",
        "Gemeinde Sankt Gerold",
        "Gemeinde Satteins",
        "Gemeinde Schlins",
        "Gemeinde Schnepfau",
        "Gemeinde Schnifis",
        "Gemeinde Schoppernau",
        "Gemeinde Schröcken",
        "Marktgemeinde Schruns",
        "Gemeinde Schwarzach",
        "Gemeinde Schwarzenberg",
        "Gemeinde Sibratsgfäll",
        "Gemeinde Silbertal",
        "Gemeinde Sonntag",
        "Gemeinde Stallehr",
        "Gemeinde Sulz",
        "Gemeinde Sulzberg",
        "Gemeinde Thüringen",
        "Gemeinde Thüringerberg",
        "Gemeinde Tschagguns",
        "Gemeinde Übersaxen",
        "Gemeinde Vandans",
        "Gemeinde Viktorsberg",
        "Gemeinde Warth",
        "Gemeinde Weiler",
        "Marktgemeinde Wolfurt",
        "Gemeinde Zwischenwasser",
        "Innsbruck"
    ]

    for area_name in area_names:
        if os.path.isfile(myhelpers.guideposts_coordinates_file(area_name)):
            continue

        signposts = fetch_signposts(area_name)
        try:
            shutil.rmtree('data/' + area_name)
        except:
            pass

        os.makedirs(myhelpers.area_directory(area_name))

        if len(signposts) < 10:
            raise Exception(f"There are no guideposts for {area_name}")

        for lat, lon, info_type, ref in signposts:
            f = open(myhelpers.guideposts_coordinates_file(area_name), "a")
            if 'VWW ' in ref or 'guidepost' == info_type:
                f.write(f"Latitude: {lat}, Longitude: {lon}, Information Type: {info_type}, Reference: {ref}\n")
            f.close()
        print("Written file with guideposts for: ", area_name)
