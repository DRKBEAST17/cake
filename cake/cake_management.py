class Cake:
    def __init__(self, name, flavor, price, size, eggless=False, decoration_type=None):
        self.name = name
        self.flavor = flavor
        self.price = price  # in INR
        self.size = size
        self.eggless = eggless  # Important for Indian market
        self.decoration_type = decoration_type

class CakeManagement:
    def __init__(self):
        self.cakes = []
        self.orders = []
        self.indian_flavors = [
            "Kesar Pista",
            "Butterscotch",
            "Mango",
            "Rose",
            "Malai",
            "Cardamom",
            "Paan",
            "Gulab Jamun Cake",
            "Rasmalai Cake"
        ]
        self.decoration_types = [
            "Traditional",
            "Mehendi Design",
            "Temple Design",
            "Peacock Theme",
            "Modern Indian"
        ]

    def add_cake(self, cake):
        self.cakes.append(cake)
        print(f"Added {cake.name} to inventory - ₹{cake.price}")

    def remove_cake(self, cake_name):
        for cake in self.cakes:
            if cake.name == cake_name:
                self.cakes.remove(cake)
                print(f"Removed {cake_name} from inventory")
                return
        print(f"Cake {cake_name} not found")

    def list_cakes(self):
        if not self.cakes:
            print("No cakes in inventory")
            return
        print("\nAvailable Cakes:")
        for cake in self.cakes:
            eggless_status = "Eggless" if cake.eggless else "Contains Egg"
            print(f"Name: {cake.name}, Flavor: {cake.flavor}, Price: ₹{cake.price}, "
                  f"Size: {cake.size}, {eggless_status}, Decoration: {cake.decoration_type}")

    def create_order(self, customer_name, cake_name, delivery_date, occasion=None):
        for cake in self.cakes:
            if cake.name == cake_name:
                order = {
                    "customer": customer_name,
                    "cake": cake,
                    "delivery_date": delivery_date,
                    "occasion": occasion,
                    "status": "Pending"
                }
                self.orders.append(order)
                print(f"Order created for {customer_name} - {cake_name}")
                print(f"Delivery scheduled for: {delivery_date}")
                return
        print(f"Cake {cake_name} not found")

    def list_orders(self):
        if not self.orders:
            print("No orders available")
            return
        print("\nCurrent Orders:")
        for order in self.orders:
            print(f"Customer: {order['customer']}")
            print(f"Cake: {order['cake'].name}")
            print(f"Delivery Date: {order['delivery_date']}")
            print(f"Occasion: {order['occasion']}")
            print(f"Status: {order['status']}")
            print("-" * 30)

    def get_available_flavors(self):
        print("\nAvailable Indian Flavors:")
        for flavor in self.indian_flavors:
            print(f"- {flavor}")

# Example Usage
if __name__ == "__main__":
    # Create cake management system
    cake_shop = CakeManagement()

    # Add sample cakes
    cake1 = Cake("Royal Rasmalai", "Rasmalai", 1200, "1 kg", True, "Traditional")
    cake2 = Cake("Kesar Special", "Kesar Pista", 1500, "1 kg", True, "Mehendi Design")
    cake3 = Cake("Mango Delight", "Mango", 900, "500g", False, "Modern Indian")

    cake_shop.add_cake(cake1)
    cake_shop.add_cake(cake2)
    cake_shop.add_cake(cake3)

    # List all cakes
    cake_shop.list_cakes()

    # Create an order
    cake_shop.create_order("Raj Kumar", "Royal Rasmalai", "2024-02-15", "Wedding")

    # Show all orders
    cake_shop.list_orders()

    # Show available flavors
    cake_shop.get_available_flavors()