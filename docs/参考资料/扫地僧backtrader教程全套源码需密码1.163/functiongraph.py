import pygal

pygal.Bar()(1, 3, 3, 7)(1, 6, 6, 4).render()
pygal.Bar()(1, 3, 3, 7)(1, 6, 6, 4).render_to_file("simple.svg")
