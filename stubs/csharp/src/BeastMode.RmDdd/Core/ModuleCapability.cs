using System;

namespace BeastMode.RmDdd.Core
{
    /// <summary>
    /// Represents a capability provided by a module.
    /// </summary>
    public class ModuleCapability
    {
        public string Name { get; }
        public string Description { get; }
        public bool Available { get; }
        public string Version { get; }
        
        public ModuleCapability(string name, string description, bool available, string version)
        {
            Name = name ?? throw new ArgumentNullException(nameof(name));
            Description = description ?? throw new ArgumentNullException(nameof(description));
            Available = available;
            Version = version ?? throw new ArgumentNullException(nameof(version));
        }
        
        public override bool Equals(object? obj)
        {
            if (obj is not ModuleCapability other) return false;
            
            return Name == other.Name &&
                   Description == other.Description &&
                   Available == other.Available &&
                   Version == other.Version;
        }
        
        public override int GetHashCode()
        {
            return HashCode.Combine(Name, Description, Available, Version);
        }
        
        public override string ToString()
        {
            return $"ModuleCapability {{ Name = '{Name}', Description = '{Description}', Available = {Available}, Version = '{Version}' }}";
        }
    }
}