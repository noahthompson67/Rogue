import pygame


def tint(surf, tint_color):
    """ adds tint_color onto surf.
    """
    surf = surf.copy()
    surf.fill((0, 0, 0, 255), None, pygame.BLEND_RGBA_MULT)
    surf.fill(tint_color[0:3] + (0,), None, pygame.BLEND_RGBA_ADD)
    return surf

def get_sprite(sheet, location, width, height, scale, flip=False):
    img = pygame.Surface((width, height), pygame.SRCALPHA)
    if sheet is not None:
        img.blit(sheet, (0, 0), (location[0], location[1], width, height))
    if flip:
        img = pygame.transform.flip(img, True, False)
    img = pygame.transform.scale(img, (width * scale, height * scale))
    return img

