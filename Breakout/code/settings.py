window_width = 1280
window_height = 780

block_map = [
    '777777777777',
    '555555555555',
    '444444444444',
    '333333333333',
    '222222222222',
    '            ',
    '            ',
    '            ',
    '            ',
]

color_legend = {
    '1' : 'blue',
    '2' : 'green',
    '3' : 'red',
    '4' : 'orange',
    '5' : 'purple',
    '6' : 'bronze',
    '7' : 'grey'
}

gap_size = 2
block_height = (window_height / len(block_map)) - gap_size
block_width = (window_width / len(block_map[0])) - gap_size
top_offest = window_height // 30

upgrades = ['speed', 'laser', 'heart', 'size']
