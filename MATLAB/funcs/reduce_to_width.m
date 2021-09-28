function [x_reduced, y_reduced] = reduce_to_width(x, y, width, lims)

% [x_reduced, y_reduced] = reduce_to_width(x, y, width, lims)
% 
% (This function is primarily used by LinePlotReducer, but has been
%  provided as a stand-alone function outside of that class so that it can
%  be used potentially in other projects. See help LinePlotReducer for 
%  more.)
%
% Reduce the data contained in x and y for display on width pixels,
% stretching from lims(1) to lims(2).
%
% For example, if x and y are 20m points long, but we only need to plot
% them over 500 pixels from x=5 to x=10, this function will return 1000
% points representing the first point of the window (x=5), the last point
% of the window (x=10), and the maxima and minima for each pixel between 
% those two points. The result is that x_reduced and y_reduced can be 
% plotted and will look exactly like x and y, without all of the waste of 
% plotting too many points.
%
% x can be n-by-1 or n-by-m with n samples of m columns (that is, there can
% be 1 x for all y or 1 x for each y.
%
% y must be n-by-m with n samples of m columns
%
% [xr, yr] = reduce_to_width(x, y, 500, [5 10]); % Reduce the data.
%
% plot(xr, yr); % This contains many fewer points than plot(x, y) but looks
%                 the same.
%
% Tucker McClure
% Copyright 2013, The MathWorks, Inc.

    % We'll need the first point to the left of the limits, the first point
    % to the right to the right of the limits, and the min and max at every
    % pixel inbetween. That's 1 + 1 + 2*(width - 2) = 2*width total points.
    n_points = 2*width;
    
    % If the data is already small, there's no need to reduce.
    if size(x, 1) <= n_points
        x_reduced = x;
        y_reduced = y;
        return;
    end

    % Reduce the data to the new axis size.
    x_reduced = nan(n_points, size(y, 2));
    y_reduced = nan(n_points, size(y, 2));
    for k = 1:size(y, 2)

        % Find the starting and stopping indices for the current limits.
        if k <= size(x, 2)
            
            % Rename the column. This actually makes stuff substantially 
            % faster than referencing x(:, k) all over the place. On my
            % timing trials, this was 20x faster than referencing x(:, k)
            % in the loop below.
            xt = x(:, k);

            % Map the lower and upper limits to indices.
            nx = size(x, 1);
            lower_limit      = binary_search(xt, lims(1), 1,           nx);
            [~, upper_limit] = binary_search(xt, lims(2), lower_limit, nx);
            
            % Make the windows mapping to each pixel.
            x_divisions = linspace(x(lower_limit, k), ...
                                   x(upper_limit, k), ...
                                   width + 1);
                               
        end

        % Create a place to store the indices we'll need.
        indices = [lower_limit, zeros(1, n_points-2), upper_limit];
        
        % For each pixel...
        right = lower_limit;
        for z = 1:width-1
            
            % Find the window bounds.
            left               = right;
            [~, right]         = binary_search(xt, ...
                                               x_divisions(z+1), ...
                                               left, upper_limit);
            
            % Get the indices of the max and min.
            yt = y(left:right, k);
            [~, max_index]     = max(yt);
            [~, min_index]     = min(yt);
            
            % Record those indices.
            indices(2*z:2*z+1) = sort([min_index max_index]) + left - 1;
            
        end

        % Sample the original x and y at the indices we found.
        x_reduced(:, k) = xt(indices);
        y_reduced(:, k) = y(indices, k);

    end
    
end

% Binary search to find boundaries of the ordered x data.
function [L, U] = binary_search(x, v, L, U)
    while L < U - 1                 % While there's space between them...
        C = floor((L+U)/2);         % Find the midpoint
        if x(C) < v                 % Move the lower or upper bound in.
            L = C;
        else
            U = C;
        end
    end
end
