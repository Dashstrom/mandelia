from threading import Thread
from PIL import Image, ImageTk
from tkinter import messagebox
import numpy as np
import time

cdef class Fractale:
  
    cdef:
        public workspace, index, photo, image, colors, pos_before_drop, stat
        public __updating, __stop_call, __thread
        public double x1, x2, y1, y2
        public unsigned long iteration_max

    def __init__(self, workspace):
        self.__updating = False
        self.workspace = workspace
        self.reset()
    
    def reset(self, keep_settings=False):
        self.stop_update()
        ratio = self.workspace.w / self.workspace.h
        self.x1 = -3 * ratio
        self.x2 = 3 * ratio
        self.y1 = -3
        self.y2 = 3
        self.__updating = self.__stop_call = False
        self.index = ""
        self.photo = self.image = self.__thread = None
        self.stat = "Aucunes statistiques à afficher" 
        if not keep_settings:
            self.iteration_max = 2000
            self.colors = (3, 1, 10)
    
    def update(self):
        if self.pos_before_drop:
            return
        if self.__thread:
            self.__stop_call = True
            self.__thread.join()
            self.__stop_call = False
        self.__thread = Thread(target=self.draw)
        self.__thread.start()
    
    def dropping(self):
        return bool(self.pos_before_drop)

    def updating(self):
        return bool(self.__updating)
    
    def stop_update(self):
        if self.updating():
            self.__stop_call = True
            self.__thread.join()
            self.__stop_call = False
            self.__thread = None

    def wait_update(self):
        if self.updating():
            self.__thread.join()
            self.__thread = None

    cpdef draw(self, drop=False):
        cdef:
            unsigned long i, iteration_max, sr, sg, sb
            unsigned long long iterations, time_taken
            int w, h 
            short x, y
            double tmp, start_at, zoom, c_r, c_i, z_r, z_i, x1, x2, y1, y2
            float vr, vg, vb
            str str_time
            unsigned char r, g, b, end
            image, data

        if (self.x2 - self.x1) == 0 or (self.y2 - self.y1) == 0:
            return
        self.__updating = True
        self.workspace.progress(0)
        iterations = 0
        
        start_time = time.time()
        iteration_max = self.iteration_max
        w, h = self.workspace.w, self.workspace.h
        x1, x2, y1, y2 = self.x1, self.x2, self.y1, self.y2
        vr, vg, vb = self.colors
        zoom = w / (x2 - x1)
        data = np.zeros((h, w, 3), dtype=np.uint8)
        data[0:h, 0:w] = (0, 0, 0)

        for x in range (w):
            c_r = x / zoom + x1

            for y in range (h):
                c_i = y / zoom + y1
                z_r = z_i = 0
                end = 0

                for i in range(iteration_max):
                    tmp = z_r
                    z_r = z_r*z_r - z_i*z_i + c_r
                    z_i = 2*z_i*tmp + c_i
                    
                    if z_r*z_r + z_i*z_i > 4:
                        end = 1
                        iterations += i
                        sr = int(vr * i)
                        sg = int(vg * i)
                        sb = int(vb * i)
                        r = sr % 256
                        g = sg % 256
                        b = sb % 256
                        data[y, x] = [r, g, b]
                        break

                if end ==0 :
                    iterations += iteration_max

                if self.__stop_call:
                    self.__updating = False
                    return

            self.workspace.progress(x / w)
            
        self.image = Image.fromarray(data, 'RGB')
        if not drop: 
            self.photo = ImageTk.PhotoImage(self.image)
            if self.index:
                self.workspace.delete(self.index)
            self.index = self.workspace.create_image(0, 0, image=self.photo, anchor="nw")

            time_taken = int((time.time()-start_time)*1000)
            if time_taken >=  86400000:
                str_time = "{}j{}h".format(time_taken//86400000, (time_taken//3600000)%24)
            elif time_taken >= 3600000:
                str_time = "{}h{}m".format(time_taken//3600000, (time_taken//60000)%60)
            elif time_taken >= 60000:
                str_time = "{}m{}s".format(time_taken//60000, (time_taken//1000)%60)
            elif time_taken >= 1000:
                str_time = "{}.{}s".format(time_taken//1000, (time_taken%1000))
            else:
                str_time = "{:.0f}ms".format(time_taken)

            self.stat = (
                f"Point 1: {x1}{'+' if y1 > 0 else ''}{y1}i\n"
                f"Point 2: {x2}{'+' if y2 > 0 else ''}{y2}i\n"
                f"Zoom: {zoom:.2e}\n"
                f"Taille de la zone: {(x2 - x1):.2e}\n"
                f"Itération maximal par pixel: {iteration_max}\n"
                f"tTemps d'éxécution: {str_time}\n"
                f"Nombre total d'itérations: {iterations:.2e}\n"
                f"Itération par milliseconde: {int(iterations / time_taken)}\n")
            self.workspace.app.main_menu.historic_menu.log(
                (x1, y1, x2, y2, iteration_max, w, h, self.stat, (vr, vg, vb)))
            messagebox.showinfo("Statistiques", self.stat)
        self.__updating = False
    
    cpdef select(
        self, double sx1, double sy1, double sx2, double sy2, drop=False
    ):
        cdef double x1, x2, y1, y2

        if sx1 > sx2:
            sx1, sx2 = sx2, sx1
        if sy1 > sy2:
            sy1, sy2 = sy2, sy1

        x1 = self.x1 + (self.x2 - self.x1) * sx1 / self.workspace.w
        x2 = self.x1 + (self.x2 - self.x1) * sx2 / self.workspace.w
        y1 = self.y1 + (self.y2 - self.y1) * sy1 / self.workspace.h
        y2 = self.y1 + (self.y2 - self.y1) * sy2  / self.workspace.h
        if self.workspace.w / (x2 - x1) > 10**17:
            return messagebox.showerror("Actualisation",
                                        "Le zoom n'est pas assez puissant")
        self.x1, self.x2, self.y1, self.y2 = x1, x2, y1, y2
        if not drop:
            self.update()
    
    cpdef set(self, keepsettings, double x1, double y1, double x2, double y2,
              unsigned long iteration_max, int w, int h, stat, rgb):
        if not keepsettings:
             self.iteration_max = iteration_max
             self.colors = rgb
        self.x1, self.y1 = x1, y1
        self.x2 = x1 + (x2 - x1) * (self.workspace.w / w)
        self.y2 = x1 + (x2 - x1) * (self.workspace.h / h)
        self.update()
    
    cpdef palette(self, float vr, float vg, float vb):
        cdef: 
            unsigned char r, g, b, x, y
            unsigned long sr, sg, sb            
        img = Image.new('RGB', (255, 30), color='black')
        for x in range(img.size[0]):
            sr = int(vr * x)
            sg = int(vg * x)
            sb = int(vb * x)
            r = sr % 256 
            g = sg % 256
            b = sb % 256
            c = (r, g, b)
            for y in range(img.size[1]):
                img.putpixel((x, y), c)
        return ImageTk.PhotoImage(img)
    
    cpdef drop(self, double x, double y):
        cdef double sx, sy, ratio
        self.pos_before_drop = self.x1, self.x2, self.y1, self.y2
        sx = (self.x1 + (self.x2 - self.x1) * x / self.workspace.w)
        sy = (self.y1 + (self.y2 - self.y1) * y / self.workspace.h)
        ratio = (self.x2 - self.x1) / (self.y2 - self.y1)
        self.x1 = sx - 3 * ratio
        self.x2 = sx + 3 * ratio
        self.y1 = sy - 3
        self.y2 = sy + 3
        print("construction du gif...")
        self.draw(drop=True)
        gif = [self.image.copy()]
        for i in range(30):
            print("{:.2f}%".format(i*100/30))
            self.select(self.workspace.w*0.25, self.workspace.h*0.25,
                        self.workspace.w*0.75, self.workspace.h*0.75,
                        drop=True)
            self.draw(drop=True)
            gif.append(self.image.copy())
        self.x1, self.x2, self.y1, self.y2 = self.pos_before_drop
        self.pos_before_drop = None
        print("100%     \ndemande de sauvegarde")
        return gif
