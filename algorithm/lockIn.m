function [Vx, Vy, V]=lockIn(inputSignal,tlist, Fm, periodNumber)
% timeInterval=tlist(2)-tlist(1);
sineWave=sin(2*pi*Fm*tlist);
cosineWave=cos(2*pi*Fm*tlist);
Vx=inputSignal.*sineWave;
Vy=inputSignal.*cosineWave;
T=periodNumber/Fm;
% X=1/T*sum(timeInterval*Vx(tlist>=0&tlist<T));
% Y=1/T*sum(timeInterval*Vy(tlist>=0&tlist<T));
X=mean(Vx(tlist>=0&tlist<periodNumber/Fm));
Y=mean(Vy(tlist>=0&tlist<periodNumber/Fm));
V=sqrt(X^2+Y^2);

end