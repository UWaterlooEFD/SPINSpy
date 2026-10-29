from dataset import Dataset

ds = Dataset('/Users/k4bhavsa/Documents/SPINSpy/spinspy/tests/reading_dir/')
u = ds.reader('u', 1)
print(u.shape)