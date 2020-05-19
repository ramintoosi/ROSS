classdef LinePlotExplorer < handle
    
% LinePlotExplorer
%
% This tool allows users to move around quickly within a 2D plot by panning
% (left clicking and dragging) or zoom (scrolling with a scroll wheel). 
% When instantiated, it will provide this ability for all axes in the
% provided figure (or current figure by default).
%
% Usage:
%
% lpe = LinePlotExplorer(h_fig, x_min, x_max); % Start LinePlotExplorer
% % ...
% lpe.Stop(); % Stop using this LinePlotExplorer.
%
% Inputs:
% 
% h_fig - Handle of figure to control (optional)
% x_min - Minimum value to show on x axis (optional)
% x_max - Maximum value to show on x axis (optional)
%
% Outputs:
%
% lpe   - LinePlotExplorer object.
%
% This object uses the figure's WindowButtonUpFcn, WindowButtonDownFcn,
% WindowButtonMotionFcn, and WindowScrollWheelFcn callbacks. If those are
% necessary for other tasks as well, callbacks can be attached to the
% LinePlotExplorer, which will pass all arguments on to the provided
% callback function.
%
% Example:
%
% lpe = LinePlotExplorer(gca);
% lpe.AttachCallback('WindowButtonDownFcn', 'disp(''clicked'');');
% 
% Or multiple callbacks can be set with a single call:
%
% lpe.AttachCallback('WindowButtonDownFcn',   'disp(''down'');', ...
%                    'WindowButtonUpFcn',     'disp(''up'');', ...
%                    'WindowButtonMotionFcn', 'disp(''moving'');', ...
%                    'WindowScrollWheelFcn',  @(~, ~) disp('scrolling'));
%
% Tucker McClure
% Copyright 2013, The MathWorks, Inc.

    properties
        
        % Figure handle
        h_fig;
        
        % Min and max values for x axis
        x_max;
        x_min;
        
        % Interactivity parameters
        button_down = false;
        button_down_point;
        button_down_axes;
        
        wbdf; % Pass-through WindowButtonDownFcn
        wbuf; % Pass-through WindowButtonUpFcn
        wbmf; % Pass-through WindowButtonMotionFcn
        wswf; % Pass-through WindowScrollWheelFcn
        
    end
    
    methods
        
        % Create a ReductiveViewer for the x and y variables.
        function o = LinePlotExplorer(varargin)
            
            % Record the figure number and min and max value on the x axis.
            if nargin < 1, o.h_fig =  gcf; else o.h_fig = varargin{1}; end;
            if nargin < 2, o.x_min = -inf; else o.x_min = varargin{2}; end;
            if nargin < 3, o.x_max =  inf; else o.x_max = varargin{3}; end;
            
            % Set the callbacks.
            set(o.h_fig, 'WindowScrollWheelFcn',  @o.Scroll, ...
                         'WindowButtonDownFcn',   @o.ButtonDown, ...
                         'WindowButtonUpFcn',     @o.ButtonUp, ...
                         'WindowButtonMotionFcn', @o.Motion);
 
        end
        
    end
    
    methods (Access = public)

        % Stop using this object to control the figure.
        function Stop(o)

            if ishandle(o.h_fig)
                
                % Clear the callbacks.
                set(o.h_fig, ...
                    'WindowButtonDownFcn',   o.wbdf, ...
                    'WindowButtonUpFcn',     o.wbuf, ...
                    'WindowButtonMotionFcn', o.wbmf, ...
                    'WindowScrollWheelFcn',  o.wswf);
                
            end
 
        end
        
        % Add a pass-through callback for one of the callbacks
        % FigureRotator hogs to itself. This way, a user can still get all
        % the info he needs from a figure's callbacks *and* use the 
        % rotator.
        function AttachCallback(o, varargin)
            
            for k = 2:2:length(varargin)
                switch varargin{k-1}
                    case 'WindowButtonDownFcn'
                        o.wbdf = varargin{k};
                    case 'WindowButtonUpFcn'
                        o.wbuf = varargin{k};
                    case 'WindowButtonMotionFcn'
                        o.wbmf = varargin{k};
                    case 'WindowScrollWheelFcn'
                        o.wswf = varargin{k};
                    otherwise
                        warning('Invalid callback attachment.');
                end
            end
            
        end
        
    end
    
    methods (Access = protected)
        
        % When the user moves the mouse wheel...
        function Scroll(o, h, event, varargin)

            % Get current axes for this figure.
            h_axes = get(o.h_fig, 'CurrentAxes');
            
            % Get where the mouse was when the user scrolled.
            point = get(h_axes, 'CurrentPoint');
            point = point(1, 1:2);
            
            % Get the old limits.
            old_x_lims = get(h_axes, 'XLim');
            old_y_lims = get(h_axes, 'YLim');
            
            % If the mouse isn't in the axes area, don't zoom.
            if    point(1) < old_x_lims(1) ...
               || point(1) > old_x_lims(2) ...
               || point(2) < old_y_lims(1) ...
               || point(2) > old_y_lims(2)
                return;
            end
            
            % Get where and in what direction user scrolled.
            exponent = double(event.VerticalScrollCount);
            
            % Calculate new limits.
            range    = diff(old_x_lims);
            alpha    = (point(1) - old_x_lims(1)) / range;
            new_lims = 2.25^exponent * range *[-alpha 1-alpha] + point(1);
            
            % Don't zoom out too far.
            new_lims = max(min(new_lims, o.x_max), o.x_min);
            
            % Update the axes.
            set(h_axes, 'XLim', new_lims);
            
            % If there's a callback attachment, execute it.
            execute_callback(o.wswf, h, event, varargin{:});

        end
        
        % The user has clicked and is holding.
        function ButtonDown(o, h, event, varargin)
            
            % Record what the axes were when the user clicked and where the
            % user clicked.
            o.button_down_axes   = get(o.h_fig, 'CurrentAxes');
            point                = get(o.button_down_axes, 'CurrentPoint');
            o.button_down_point  = point(1, 1:2);
            o.button_down        = true;
            
            % If there's a callback attachment, execute it.
            execute_callback(o.wbdf, h, event, varargin{:});
            
        end
        
        % The user has released the button.
        function ButtonUp(o, h, event, varargin)
            
            o.button_down = false;
            
            % If there's a callback attachment, execute it.
            execute_callback(o.wbuf, h, event, varargin{:});
            
        end
        
        % When the user moves the mouse with the button down, pan.
        function Motion(o, h, event, varargin)
            
            if o.button_down

                % Get the mouse position and movement from original point.
                point    = get(o.button_down_axes, 'CurrentPoint');
                movement = point(1, 1) - o.button_down_point(1);
                xlims    = get(o.button_down_axes, 'XLim');
                
                % Don't let the user pan too far.
                new_lims = xlims - movement;
                if new_lims(1) < o.x_min
                    new_lims = o.x_min + [0 diff(new_lims)];
                end
                if new_lims(2) > o.x_max
                    new_lims = o.x_max - [diff(new_lims) 0];
                end

                % Update the axes.
                set(o.button_down_axes, 'XLim', new_lims);

            end

            % If there's a callback attachment, execute it.
            execute_callback(o.wbmf, h, event, varargin{:});
            
        end
                
    end
    
end

% Execute whatever callback was requested.
function execute_callback(cb, h, event, varargin)
    if ~isempty(cb)
        if isa(cb, 'function_handle')
            cb(h, event)
        elseif iscell(cb)
            cb(h, event, varargin{:})
        else
            eval(cb);
        end
    end
end
