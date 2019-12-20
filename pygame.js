// Transcrypt'ed from Python, 2019-12-04 22:46:38
import {AssertionError, AttributeError, BaseException, DeprecationWarning, Exception, IndexError, IterableError, KeyError, NotImplementedError, RuntimeWarning, StopIteration, UserWarning, ValueError, Warning, __JsIterator__, __PyIterator__, __Terminal__, __add__, __and__, __call__, __class__, __envir__, __eq__, __floordiv__, __ge__, __get__, __getcm__, __getitem__, __getslice__, __getsm__, __gt__, __i__, __iadd__, __iand__, __idiv__, __ijsmod__, __ilshift__, __imatmul__, __imod__, __imul__, __in__, __init__, __ior__, __ipow__, __irshift__, __isub__, __ixor__, __jsUsePyNext__, __jsmod__, __k__, __kwargtrans__, __le__, __lshift__, __lt__, __matmul__, __mergefields__, __mergekwargtrans__, __mod__, __mul__, __ne__, __neg__, __nest__, __or__, __pow__, __pragma__, __proxy__, __pyUseJsNext__, __rshift__, __setitem__, __setproperty__, __setslice__, __sort__, __specialattrib__, __sub__, __super__, __t__, __terminal__, __truediv__, __withblock__, __xor__, abs, all, any, assert, bool, bytearray, bytes, callable, chr, copy, deepcopy, delattr, dict, dir, divmod, enumerate, filter, float, getattr, hasattr, input, int, isinstance, issubclass, len, list, map, max, min, object, ord, pow, print, property, py_TypeError, py_iter, py_metatype, py_next, py_reversed, py_typeof, range, repr, round, set, setattr, sorted, str, sum, tuple, zip} from './org.transcrypt.__runtime__.js';
var __name__ = '__main__';
export var QUIT = false;
export var Events =  __class__ ('Events', [object], {
	__module__: __name__,
	get py_get () {return __get__ (this, function (self) {
		return [];
	});}
});
export var Display =  __class__ ('Display', [object], {
	__module__: __name__,
	get set_mode () {return __get__ (this, function (self, size) {
		return DisplayRender (size);
	});},
	get flip () {return __get__ (this, function () {
		// pass;
	});}
});
export var DisplayRender =  __class__ ('DisplayRender', [object], {
	__module__: __name__,
	get __init__ () {return __get__ (this, function (self, size) {
		self.canvas = document.getElementById ('myCanvas');
		self.ctx = self.canvas.getContext ('2d');
		self.size = size;
		self.canvas.width = size;
		self.canvas.height = size;
	});},
	get fill () {return __get__ (this, function (self, color) {
		self.ctx.fillStyle = '#FF0000';
		self.ctx.fillRect (0, 0, self.size, self.size);
		// pass;
	});},
	get blit () {return __get__ (this, function (self, img, dest, source) {
		self.ctx.drawImage (img, source [0], source [1], source [2], source [3], dest [0], dest [1], dest [2], dest [3]);
	});}
});
export var DisplayDraw =  __class__ ('DisplayDraw', [object], {
	__module__: __name__,
	get rect () {return __get__ (this, function (self, ctx, color, rect) {
		var hexcolor = '#';
		for (var c of color) {
			hexcolor += hex (c).__getslice__ (2, null, 1);
		}
		ctx.fillStyle = hexcolor;
		ctx.fillRect (rect [0], rect [1], rect [2], rect [3]);
	});}
});
export var ImageLoader =  __class__ ('ImageLoader', [object], {
	__module__: __name__,
	get load () {return __get__ (this, function (self, path) {
		var img = new Image ();
		img.src = path;
		return img;
	});}
});
export var display = Display ();
export var event = Events ();
export var draw = DisplayDraw ();
export var image = ImageLoader ();
export var init = function () {
	// pass;
};
export var Rect = function (x, y, width, height) {
	return tuple ([x, y, width, height]);
};

//# sourceMappingURL=pygame.map