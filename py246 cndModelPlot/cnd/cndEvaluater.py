import numpy as np

class CndEvaluater:
    def __init__ (this, result=None):
        this.n = this.tp = this.fp = this.fn = this.tn = 0
        if result is not None:
            this += result
    
    def __iadd__ (this, result):
        for *_, y, yhat in zip(*result):
            if y == yhat:
                if y is not None: this.tp += 1
                else: this.tn += 1
            else:
                if y is not None: this.fp += 1
                if yhat is not None: this.fn += 1
            this.n += 1
        return this
    
    @property
    def accuracy (this):
        if not this.n:return np.nan
        return round(np.divide((this.tp + this.tn), this.n), 5)
    
    @property
    def precision (this):
        if not (this.tp + this.fp):return np.nan
        return round(np.divide(this.tp, (this.tp + this.fp)), 5)
    
    @property
    def recall (this):
        if not (this.tp + this.fn):return np.nan
        return round(np.divide(this.tp, (this.tp + this.fn)), 5)
    
    @property
    def data (this):
        return {'n' : this.n, 'tp' : this.tp, 'fp' : this.fp, 'fn' : this.fn, 'tn' : this.tn, 
                'accuracy' : this.accuracy, 'precision' : this.precision, 'recall' : this.recall}
    
    def _repr_pretty_(this, pp, cycle):
        plain = get_ipython().display_formatter.formatters['text/plain']
        return plain.type_printers[dict](this.data, pp, cycle)
    
    def __repr__ (this):
        return str(this.data)
    
    __str__ = __repr__
    
    def loads (this, value):
        this.n, this.tp, this.fp, this.fn, this.tn = value
        return this
    def dumps (this):
        return [this.n, this.tp, this.fp, this.fn, this.tn]

def loadEva (value):
    return CndEvaluater().loads(value)