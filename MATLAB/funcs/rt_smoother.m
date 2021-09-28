function ps = rt_smoother(y,win_length)
% This function smooths y by convolving it by a Gaussian widow

% default window length is considered 5
if nargin < 2
    win_length = 5;
end
win_alpha = 1;

% a Gaussian window with win_length points
win = gausswin(win_length,win_alpha);
win = win/sum(win);
ps = conv(y,win,'same');