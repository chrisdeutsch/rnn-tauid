from collections import namedtuple
import pickle


Samples = namedtuple("Samples", ["sig_train", "sig_test",
                                 "bkg_train", "bkg_test"])


class Plot(object):
    def __init__(self):
        self.fig = None


    def plot(self, samples, scores=None):
        """
        Returns:
        matplotlib figure? axes?
        """
        raise NotImplementedError("plot() needs to be defined in derived class")


    def save_raw(self, filename):
        """
        Returns:
        save raw data for replotting
        """
        if self.fig:
            with open(filename, "wb") as outf:
                pickle.dump(self.fig, outf)
        else:
            raise RuntimeError("Call plot() before save_raw()")


# Define requirements for plot to know what to load
