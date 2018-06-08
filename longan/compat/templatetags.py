def coords_for_imagemap(crop):
    return str(str(crop.get('tl')[0]) + "," + str(crop.get('tl')[1]) + "," +
               str(crop.get('tr')[0]) + "," + str(crop.get('tr')[1]) + "," +
               str(crop.get('br')[0]) + "," + str(crop.get('br')[1]) + "," +
               str(crop.get('bl')[0]) + "," + str(crop.get('bl')[1]))
