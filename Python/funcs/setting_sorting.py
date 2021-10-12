class Setting:
    def __init__(self):
        self.alignment_max_shift = 10 # int pos 1-size(spike_mat,2)/2 -1
        self.alignment_n_peaks = 3 # int pos 1-size(spike_mat,2)
        self.alignment_number_of_hist_bins = 75 
        self.alignment_comparison_mode = 'magnitude' # index, magnitude

        # t-distribution sorting
        self.sort_type = 't dist'
        self.sort_nu = 20 #float 0-inf
        self.sort_g_max = 9 #int g_min-inf
        self.sort_g_min = 1 #int 1-g_max
        self.sort_max_iter = 500 #int pos 1-inf
        self.sort_u_lim = 0.01 #float 0-1
        self.sort_N = 15 #float 0-inf
        self.sort_n_pca = 5 #int 1-size(spike_mat,2)
        self.sort_n_pca_max = 5
        self.sort_random_seed = 561371 #any
        self.sort_error = 1e-1 # float
        self.sort_uni_Gama = False # boolean %NOTE: not provided in the ui yet
    
    def assign_alignment(self, max_shift, n_peaks, number_of_hist_bins, comparison_mode):
        self.alignment_max_shift = max_shift
        self.alignment_n_peaks = n_peaks
        self.alignment_number_of_hist_bins = number_of_hist_bins
        self.alignment_comparison_mode = comparison_mode
    
    def assign_sort(self, sort_type, nu, g_max, g_min, max_iter, u_lim, N, n_pca, n_pca_max, random_seed, 
                    error, uni_Gama):
        self.sort_type = sort_type
        self.sort_nu = nu
        self.sort_g_max = g_max
        self.sort_g_min = g_min
        self.sort_max_iter = max_iter
        self.sort_u_lim = u_lim
        self.sort_N = N
        self.sort_n_pca = n_pca
        self.sort_n_pca_max = n_pca_max
        self.sort_random_seed = random_seed
        self.sort_error = error
        self.sort_uni_Gama = uni_Gama