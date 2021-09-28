function pixels = get_axes_width(h)

% pixels = get_axes_width(h)
% 
% Returns the width of the axes object, h, in pixels.
%
% --- Change Log ---
%
% 2014-06-04: Avoids changing axes units where possible.
% Changes copyright 2014 Tucker McClure.
% 
% 2013-03-15: Original. Copyright 2013, The MathWorks, Inc.
%
% ---
%
% Copyright 2014, The MathWorks, Inc. and Tucker McClure

    % Record the current axes units setting.
    axes_units = get(h, 'Units');

    % We should change the units only if they're not already set to pixels.
    change_units = ~strcmp(axes_units, 'pixels');
    
    % Change axes units to pixels.
    if change_units
        set(h, 'Units', 'pixels'); % This triggers other callbacks.
    end

    % Get axes width in pixels.
    axes_position = get(h, 'Position');
    pixels = round(axes_position(3));

    % Return the units.
    if change_units
        set(h, 'Units', axes_units); % This triggers other callbacks.
    end
    
end
