"""
Лабораторная работа 5: Алгоритмы отсечения отрезков и многоугольников
Вариант 12
Алгоритмы:
1. Алгоритм средней точки для отсечения отрезков прямоугольным окном
2. Алгоритм отсечения отрезков выпуклым многоугольником
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import math


class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y
    
    def __repr__(self):
        return f"Point({self.x}, {self.y})"


class Line:
    def __init__(self, p1, p2):
        self.p1 = p1
        self.p2 = p2
    
    def __repr__(self):
        return f"Line({self.p1}, {self.p2})"


class Rectangle:
    def __init__(self, xmin, ymin, xmax, ymax):
        self.xmin = min(xmin, xmax)
        self.ymin = min(ymin, ymax)
        self.xmax = max(xmin, xmax)
        self.ymax = max(ymin, ymax)


def midpoint_clipping_algorithm(line, rect, epsilon=0.001, max_iterations=50):

    p1 = Point(line.p1.x, line.p1.y)
    p2 = Point(line.p2.x, line.p2.y)
    
    def is_inside(p):
        return (rect.xmin <= p.x <= rect.xmax and 
                rect.ymin <= p.y <= rect.ymax)
    
    def is_outside(p):
        return (p.x < rect.xmin or p.x > rect.xmax or 
                p.y < rect.ymin or p.y > rect.ymax)
    
    def both_ends_same_side_outside(p1, p2):
        if p1.x < rect.xmin and p2.x < rect.xmin:
            return True
        if p1.x > rect.xmax and p2.x > rect.xmax:
            return True
        if p1.y < rect.ymin and p2.y < rect.ymin:
            return True
        if p1.y > rect.ymax and p2.y > rect.ymax:
            return True
        return False
    
    if is_inside(p1) and is_inside(p2):
        return Line(p1, p2)
    
    if both_ends_same_side_outside(p1, p2):
        return None
    
    iteration = 0
    while iteration < max_iterations:
        iteration += 1
        
        while is_outside(p1) and not both_ends_same_side_outside(p1, p2):
            mid = Point((p1.x + p2.x) / 2, (p1.y + p2.y) / 2)
            
            dist = math.sqrt((p2.x - p1.x)**2 + (p2.y - p1.y)**2)
            if dist < epsilon:
                break
            
            if is_inside(mid):
                p2 = mid
            else:
                p1 = mid
        
        p2 = Point(line.p2.x, line.p2.y)
        
        while is_outside(p2) and not both_ends_same_side_outside(p1, p2):
            mid = Point((p1.x + p2.x) / 2, (p1.y + p2.y) / 2)
            
            dist = math.sqrt((p2.x - p1.x)**2 + (p2.y - p1.y)**2)
            if dist < epsilon:
                break
            
            if is_inside(mid):
                p1 = mid
            else:
                p2 = mid
        
        if is_inside(p1) and is_inside(p2):
            return Line(p1, p2)
        
        if both_ends_same_side_outside(p1, p2):
            return None
        
        dist = math.sqrt((p2.x - p1.x)**2 + (p2.y - p1.y)**2)
        if dist < epsilon:
            if is_inside(p1) or is_inside(p2):
                return Line(p1, p2)
            return None
    
    if is_inside(p1) and is_inside(p2):
        return Line(p1, p2)
    
    if both_ends_same_side_outside(p1, p2):
        return None
    
    if is_inside(p1) or is_inside(p2):
        return Line(p1, p2)
    
    return None


def cyrus_beck_polygon_clipping(line, polygon):

    n = len(polygon)
    if n < 3:
        return None
    
    dx = line.p2.x - line.p1.x
    dy = line.p2.y - line.p1.y
    
    t_enter = 0.0
    t_exit = 1.0
    
    for i in range(n):
        p1 = polygon[i]
        p2 = polygon[(i + 1) % n]
        
        edge_x = p2.x - p1.x
        edge_y = p2.y - p1.y
        
        normal_x = -edge_y
        normal_y = edge_x
        
        w_x = line.p1.x - p1.x
        w_y = line.p1.y - p1.y
        
        numerator = -(normal_x * w_x + normal_y * w_y)
        
        denominator = normal_x * dx + normal_y * dy
        
        if abs(denominator) < 1e-10:
            if numerator < 0:
                return None
        else:
            t = numerator / denominator
            
            if denominator < 0:
                t_enter = max(t_enter, t)
            else:
                t_exit = min(t_exit, t)
        
        if t_enter > t_exit:
            return None
    
    if t_enter > t_exit or t_exit < 0 or t_enter > 1:
        return None
    
        clipped_p1 = Point(
        line.p1.x + t_enter * dx,
        line.p1.y + t_enter * dy
    )
    clipped_p2 = Point(
        line.p1.x + t_exit * dx,
        line.p1.y + t_exit * dy
    )
    
    return Line(clipped_p1, clipped_p2)


class ClippingApp:
    
    def __init__(self, root):
        self.root = root
        self.root.title("Лабораторная работа 5 - Алгоритмы отсечения (Вариант 12)")
        self.root.geometry("1400x800")
        
        self.lines = []
        self.rect_window = None
        self.polygon_window = []
        
        self.scale = 1.0
        self.offset_x = 0
        self.offset_y = 0
        self.canvas_width = 900
        self.canvas_height = 700
        
        self.setup_ui()
        
    def setup_ui(self):
        main_container = ttk.Frame(self.root)
        main_container.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        left_panel = ttk.Frame(main_container, width=450)
        left_panel.pack(side=tk.LEFT, fill=tk.BOTH, padx=(0, 5))
        left_panel.pack_propagate(False)
        
        title_label = ttk.Label(left_panel, text="Вариант 12", font=("Arial", 14, "bold"))
        title_label.pack(pady=5)
        
        subtitle_label = ttk.Label(left_panel, text="Алгоритм средней точки\nОтсечение выпуклым многоугольником", 
                                   font=("Arial", 10), justify=tk.CENTER)
        subtitle_label.pack(pady=5)
        
        load_button = ttk.Button(left_panel, text="Загрузить данные из файла", command=self.load_from_file)
        load_button.pack(pady=5, fill=tk.X, padx=10)
        
        ttk.Separator(left_panel, orient=tk.HORIZONTAL).pack(fill=tk.X, pady=10)
        
        lines_frame = ttk.LabelFrame(left_panel, text="Отрезки")
        lines_frame.pack(fill=tk.BOTH, expand=True, pady=5, padx=10)
        
        self.lines_text = tk.Text(lines_frame, height=10, width=50)
        self.lines_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(5, 0), pady=5)
        
        lines_scrollbar = ttk.Scrollbar(lines_frame, command=self.lines_text.yview)
        lines_scrollbar.pack(side=tk.RIGHT, fill=tk.Y, pady=5, padx=(0, 5))
        self.lines_text.config(yscrollcommand=lines_scrollbar.set)
        
        rect_frame = ttk.LabelFrame(left_panel, text="Прямоугольное окно (Xmin Ymin Xmax Ymax)")
        rect_frame.pack(fill=tk.X, pady=5, padx=10)
        
        self.rect_entry = ttk.Entry(rect_frame)
        self.rect_entry.pack(fill=tk.X, padx=5, pady=5)
        self.rect_entry.insert(0, "50 50 250 200")
        
        polygon_frame = ttk.LabelFrame(left_panel, text="Выпуклый многоугольник")
        polygon_frame.pack(fill=tk.BOTH, expand=True, pady=5, padx=10)
        
        self.polygon_text = tk.Text(polygon_frame, height=8, width=50)
        self.polygon_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(5, 0), pady=5)
        
        polygon_scrollbar = ttk.Scrollbar(polygon_frame, command=self.polygon_text.yview)
        polygon_scrollbar.pack(side=tk.RIGHT, fill=tk.Y, pady=5, padx=(0, 5))
        self.polygon_text.config(yscrollcommand=polygon_scrollbar.set)
        
        buttons_frame = ttk.Frame(left_panel)
        buttons_frame.pack(fill=tk.X, pady=10, padx=10)
        
        visualize_button = ttk.Button(buttons_frame, text="Визуализировать", command=self.visualize)
        visualize_button.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=(0, 5))
        
        clear_button = ttk.Button(buttons_frame, text="Очистить", command=self.clear_all)
        clear_button.pack(side=tk.RIGHT, expand=True, fill=tk.X)
        
        right_panel = ttk.Frame(main_container)
        right_panel.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        self.canvas = tk.Canvas(right_panel, bg="white", width=self.canvas_width, height=self.canvas_height)
        self.canvas.pack(fill=tk.BOTH, expand=True)
        
        self.load_example_data()
    
    def load_example_data(self):
        example_lines = """0 0 300 300
50 300 300 50
150 0 150 300
0 150 300 150
100 100 200 250
250 100 50 200"""
        self.lines_text.insert("1.0", example_lines)
        
        example_polygon = """300 300
500 300
500 500
300 500"""
        self.polygon_text.insert("1.0", example_polygon)
    
    def load_from_file(self):
        file_path = filedialog.askopenfilename(
            title="Выберите файл с данными",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        )
        
        if not file_path:
            return
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            if len(lines) < 2:
                messagebox.showerror("Ошибка", "Недостаточно данных в файле")
                return
            
            n = int(lines[0].strip())
            
            self.lines_text.delete("1.0", tk.END)
            for i in range(1, n + 1):
                if i < len(lines):
                    self.lines_text.insert(tk.END, lines[i].strip() + "\n")
            
            if n + 1 < len(lines):
                rect_data = lines[n + 1].strip()
                self.rect_entry.delete(0, tk.END)
                self.rect_entry.insert(0, rect_data)
            
            if n + 2 < len(lines):
                self.polygon_text.delete("1.0", tk.END)
                for i in range(n + 2, len(lines)):
                    self.polygon_text.insert(tk.END, lines[i].strip() + "\n")
            
            messagebox.showinfo("Успех", "Данные успешно загружены из файла")
            
        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка при чтении файла: {str(e)}")
    
    def parse_input(self):
        try:
            self.lines = []
            lines_text = self.lines_text.get("1.0", tk.END).strip()
            for line in lines_text.split("\n"):
                if line.strip():
                    coords = list(map(float, line.split()))
                    if len(coords) == 4:
                        self.lines.append(Line(
                            Point(coords[0], coords[1]),
                            Point(coords[2], coords[3])
                        ))
            
            rect_text = self.rect_entry.get().strip()
            rect_coords = list(map(float, rect_text.split()))
            if len(rect_coords) == 4:
                self.rect_window = Rectangle(
                    rect_coords[0], rect_coords[1],
                    rect_coords[2], rect_coords[3]
                )
            
            self.polygon_window = []
            polygon_text = self.polygon_text.get("1.0", tk.END).strip()
            for line in polygon_text.split("\n"):
                if line.strip():
                    coords = list(map(float, line.split()))
                    if len(coords) == 2:
                        self.polygon_window.append(Point(coords[0], coords[1]))
            
            return True
        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка при парсинге данных: {str(e)}")
            return False
    
    def calculate_scale(self):
        if not self.lines:
            self.scale = 1.0
            self.offset_x = 50
            self.offset_y = 50
            return

        all_x = []
        all_y = []
        
        for line in self.lines:
            all_x.extend([line.p1.x, line.p2.x])
            all_y.extend([line.p1.y, line.p2.y])
        
        if self.rect_window:
            all_x.extend([self.rect_window.xmin, self.rect_window.xmax])
            all_y.extend([self.rect_window.ymin, self.rect_window.ymax])
        
        for point in self.polygon_window:
            all_x.append(point.x)
            all_y.append(point.y)
        
        if not all_x or not all_y:
            self.scale = 1.0
            self.offset_x = 50
            self.offset_y = 50
            return
        
        min_x, max_x = min(all_x), max(all_x)
        min_y, max_y = min(all_y), max(all_y)
        
        width = max_x - min_x
        height = max_y - min_y
        
        if width == 0 or height == 0:
            self.scale = 1.0
        else:
            scale_x = (self.canvas_width - 100) / width
            scale_y = (self.canvas_height - 100) / height
            self.scale = min(scale_x, scale_y)
        
        self.offset_x = 50 - min_x * self.scale
        self.offset_y = self.canvas_height - 50 + min_y * self.scale
    
    def to_canvas_coords(self, x, y):
        canvas_x = x * self.scale + self.offset_x
        canvas_y = self.offset_y - y * self.scale
        return canvas_x, canvas_y
    
    def draw_coordinate_system(self):
        self.canvas.create_line(0, self.canvas_height // 2, self.canvas_width, 
                               self.canvas_height // 2, fill="lightgray", dash=(2, 2))
        self.canvas.create_line(self.canvas_width // 2, 0, self.canvas_width // 2, 
                               self.canvas_height, fill="lightgray", dash=(2, 2))
        
        for i in range(0, self.canvas_width, 50):
            self.canvas.create_line(i, 0, i, self.canvas_height, fill="#f0f0f0")
        for i in range(0, self.canvas_height, 50):
            self.canvas.create_line(0, i, self.canvas_width, i, fill="#f0f0f0")
    
    def visualize(self):
        if not self.parse_input():
            return
        
        if not self.lines:
            messagebox.showwarning("Предупреждение", "Не заданы отрезки для отсечения")
            return
        
        self.canvas.delete("all")
        
        self.calculate_scale()
        
        self.draw_coordinate_system()
        
        for line in self.lines:
            x1, y1 = self.to_canvas_coords(line.p1.x, line.p1.y)
            x2, y2 = self.to_canvas_coords(line.p2.x, line.p2.y)
            self.canvas.create_line(x1, y1, x2, y2, fill="red", width=2)
        
        if self.rect_window:
            x1, y1 = self.to_canvas_coords(self.rect_window.xmin, self.rect_window.ymin)
            x2, y2 = self.to_canvas_coords(self.rect_window.xmax, self.rect_window.ymax)
            self.canvas.create_rectangle(x1, y1, x2, y2, outline="blue", width=3)
            
            for line in self.lines:
                clipped = midpoint_clipping_algorithm(line, self.rect_window)
                if clipped:
                    x1, y1 = self.to_canvas_coords(clipped.p1.x, clipped.p1.y)
                    x2, y2 = self.to_canvas_coords(clipped.p2.x, clipped.p2.y)
                    self.canvas.create_line(x1, y1, x2, y2, fill="green", width=3)
            
            self.canvas.create_text(20, 20, text="Алгоритм средней точки:", 
                                   anchor=tk.W, font=("Arial", 10, "bold"))
            self.canvas.create_line(20, 35, 50, 35, fill="red", width=2)
            self.canvas.create_text(55, 35, text="Исходные отрезки", anchor=tk.W)
            self.canvas.create_line(20, 55, 50, 55, fill="blue", width=3)
            self.canvas.create_text(55, 55, text="Прямоугольное окно", anchor=tk.W)
            self.canvas.create_line(20, 75, 50, 75, fill="green", width=3)
            self.canvas.create_text(55, 75, text="Видимые части", anchor=tk.W)
        
        if len(self.polygon_window) >= 3:
            polygon_coords = []
            for point in self.polygon_window:
                x, y = self.to_canvas_coords(point.x, point.y)
                polygon_coords.extend([x, y])
            self.canvas.create_polygon(polygon_coords, outline="purple", fill="", width=3)
            
            for line in self.lines:
                clipped = cyrus_beck_polygon_clipping(line, self.polygon_window)
                if clipped:
                    x1, y1 = self.to_canvas_coords(clipped.p1.x, clipped.p1.y)
                    x2, y2 = self.to_canvas_coords(clipped.p2.x, clipped.p2.y)
                    self.canvas.create_line(x1, y1, x2, y2, fill="orange", width=3)
            
            legend_y_start = 100
            self.canvas.create_text(20, legend_y_start, 
                                   text="Алгоритм Кируса-Бека:", 
                                   anchor=tk.W, font=("Arial", 10, "bold"))
            self.canvas.create_line(20, legend_y_start + 15, 50, legend_y_start + 15, 
                                   fill="red", width=2)
            self.canvas.create_text(55, legend_y_start + 15, 
                                   text="Исходные отрезки", anchor=tk.W)
            self.canvas.create_line(20, legend_y_start + 35, 50, legend_y_start + 35, 
                                   fill="purple", width=3)
            self.canvas.create_text(55, legend_y_start + 35, 
                                   text="Выпуклый многоугольник", anchor=tk.W)
            self.canvas.create_line(20, legend_y_start + 55, 50, legend_y_start + 55, 
                                   fill="orange", width=3)
            self.canvas.create_text(55, legend_y_start + 55, 
                                   text="Видимые части", anchor=tk.W)
    
    def clear_all(self):
        self.lines_text.delete("1.0", tk.END)
        self.rect_entry.delete(0, tk.END)
        self.polygon_text.delete("1.0", tk.END)
        self.canvas.delete("all")
        self.lines = []
        self.rect_window = None
        self.polygon_window = []


def main():
    root = tk.Tk()
    app = ClippingApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()

