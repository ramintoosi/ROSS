function h = reduce_plot(varargin)

% h = reduce_plot(varargin)
% 
% This is a light wrapper function for LinePlotReducer. It accepts exactly
% the same arguments, but returns plot handles instead of a LinePlotReducer
% object. See 'help LinePlotReducer'.
%
% Tucker McClure
% Copyright 2013, The MathWorks, Inc.

    lpr = LinePlotReducer(varargin{:});
    h = lpr.h_plot;

end
