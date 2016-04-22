#include <stdexcept>
#include <sstream>
#include <iostream>
#include <fstream>
#include <cstring>
#include <vector>
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>

// CODE ADAPTED FROM ROWLEY GROUP ACFCalculator:
// https://github.com/RowleyGroup/ACFCalculator

// compile: g++ ACF_parse.cpp -o acf.x 

// Usage: ./acf.x -f input_timeseries.dat -s numSamples -n nCorr -d timestep_dt -o out_acf_file.dat [-c cutoff] 

double *calcCorrelation(double *y, int nSamples, int nCorr)
{
  double *corr=new double[nCorr];
  int t;
  int ttoMax;

  for(int i=0;i<nCorr;++i)
    {
      corr[i]=0.0;
    }

  for(int i=0;i<nSamples;++i)
    {
      ttoMax=nSamples;
      
      if(i+nCorr<nSamples)
        ttoMax=i+nCorr;

      for(int j=i;j<ttoMax;++j)
        {
          t=j-i;
          corr[t]+=y[i]*y[j];
        }
    }

  for(int i=0;i<nCorr;++i)
    {
      corr[i]=corr[i]/(nSamples-i);
    }

  return(corr);
}

double variance(double *y, int nSamples)
{
  double v2=0.0;
  for(int i=0;i<nSamples;++i)
    v2+=y[i]*y[i];
  v2/=nSamples;
  return(v2);
}

double calc_average(double *y, int nSamples)
{
  double avg=0.0;

  for(int i=0;i<nSamples;++i)
    {
      avg+=y[i];
    }
  avg/=nSamples;

  return(avg);
}

void subtract_average(double *y, int nSamples)
{
  double avg=calc_average(y, nSamples);

  for(int i=0;i<nSamples;++i)
    y[i]-=avg;
}

double integrateCorr(double *acf, int nCorr, double timestep)
{
  double I=0.0;

  for(int i=0;i<nCorr-1;++i)
    {
      I+=0.5*(acf[i]+acf[i+1])*timestep;
    }
  return(I);
}

double integrateCorrCutoff(double *acf, int nCorr, double timestep,  double cutoff)
{
  double I=0.0;

  for(int i=0;i<nCorr-1;++i)
    {
      if(acf[i]<cutoff*acf[0])
	break;
      I+=0.5*(acf[i]+acf[i+1])*timestep;
    }
  return(I);
}

std::vector<double> readSeries(char *fname, int &numSamples, int field)
{
  std::ifstream datafile(fname, std::ifstream::in);
  std::vector<double> series;
  std::string line;
  std::string item;
  std::istringstream iss;

  numSamples=0;

  while(getline(datafile,line))
    {
      if(line.at(0)!='#'|| line.at(0)!='@')
        {
          try
            {
              double dbl;
              int nchar=0;
              char *cline=(char *) line.c_str();

              for(int i=1;i<=field;++i)
                {
                  if(sscanf(cline, "%lf%n", &dbl, &nchar) == 0)
                    break;
                  cline+=nchar;
                }
              series.push_back(dbl*1.0);
              ++numSamples;
            }
          catch (std::exception& e)
            {
              break;
            }
        }
    }

  return(series);
}

// Help function
void showhelpinfo(char *s);

void showhelpinfo(char *s)
{
  printf("Usage: ./acf.x -f input_timeseries.dat -s numSamples -n nCorr -d timestep_dt -o out_acf_file.dat [-c cutoff]\n");
}

// Main
int main(int argc, char *argv[])
{
  double *acf,*timeSeries;
  std::vector<double> series;
  int field=2;
  int numSamples = 0;
  int nCorr = 0;
  double cutoff=0;
  char *filename;
  char *outfile=NULL;
  FILE * pFile;
  double dt=0;
  double var;
  double ans;

  // Check minimum arguments are provided
  if(argc <11)
  {
    showhelpinfo(argv[0]);
    exit(1);
  }

  // Parse command line
  char tmp;
  while ((tmp = getopt(argc, argv, "f:s:n:d:o:c:")) != -1) {
    switch (tmp) {
    case 'f':
      filename = optarg;
      if (!std::ifstream(filename))
      {
      printf("Error: cannot find %s\n",filename);
      showhelpinfo(argv[0]);
      exit(1);
      }
      break;
    case 's':
      numSamples = atoi(optarg);
      if (numSamples==0)
      {
      printf("Error: numSamples is nil\n");
      showhelpinfo(argv[0]);
      exit(1);
      }
      break;
    case 'n':
      nCorr = atoi(optarg);
      if (nCorr==0 or nCorr>numSamples)
      {
      printf("Error: nCorr must be non-zero and less than numSamples\n");
      showhelpinfo(argv[0]);
      exit(1);
      }
      break;
    case 'd':
      dt = atof(optarg);
      if (dt==0)
      {
      printf("Error: timeStep is nil\n");
      showhelpinfo(argv[0]);
      exit(1);
      }
      break;
    case 'c':
      cutoff = atof(optarg);
      break;
    case 'o':
      outfile = optarg;
      break;
    }
  }

  if (outfile==NULL)
  {
  std::string acf_fname_str="acf_out.dat";
  //printf("%s\n",acf_fname_str.c_str());
  outfile = new char [acf_fname_str.length()+1];
  std::strcpy(outfile, acf_fname_str.c_str());
  }

  // For debug - print options
  //printf("filename %s\n", filename);
  //printf("numSamples %d\n", numSamples);
  //printf("nCorr %d\n", nCorr);
  //printf("timeStep %lf\n", dt);
  //printf("cutoff %lf\n", cutoff);
  //printf("outfile %s\n", outfile);

  //Load timeseries file
  series=readSeries(filename, numSamples, field);
  timeSeries=&series[0];

  //Subtract avg
  subtract_average(timeSeries, numSamples);

  //Calculate ACF
  acf=calcCorrelation(timeSeries, numSamples, nCorr);

  // Calculate variance
  var=variance(timeSeries, numSamples);

  //Print out ACF
  pFile = fopen(outfile,"w");
  for (int i = 0; i <nCorr; ++i)
	fprintf(pFile,"%lf %lf\n",(i*dt),acf[i]); 
	//std::cout <<(i*dt)<< " "<<acf[i]<<std::endl;
  fclose(pFile);

  //Calculate integral of ACF
  if (cutoff>0)
  {
	ans=integrateCorrCutoff(acf, nCorr, dt,  cutoff);
  }
  else
  {
	ans=integrateCorr(acf,nCorr,dt);
  }

  //Print integral value
  std::cout<<"D(cms^2/s): "<<((var*var*1.0e-20)/(ans*1.0e-12))*1.e4<<" variance (A^2): "<<(var)<<" integral (A^2 ps): "<<(ans)<<std::endl;

}
