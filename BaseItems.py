#These are some simple items that are common in the world.

import World, ToastWrangler, InputHandler, Logger, Item

class Revolver(Item.InventoryItem):
    def __init__(self):
        Item.InventoryItem.__init__(self)
        self.description = 'a revolver'

class SheriffBadge(Item.InventoryItem):
    def __init__(self):
        Item.InventoryItem.__init__(self)
        self.description = 'a sheriff\'s badge'
