function [tlist,outputSignal]=MovingAveragerFilter(windowWidth, inputSignal, tlist)
outputSignal=zeros(1, length(inputSignal)-windowWidth+1);
for i=1:length(outputSignal)
outputSignal(i)=mean(inputSignal(i:i+windowWidth-1));
end
tlist=tlist(1:end-windowWidth+1);
end