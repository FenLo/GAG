const { SlashCommandBuilder, PermissionFlagsBits } = require('discord.js');

module.exports = {
    data: new SlashCommandBuilder()
        .setName('unlock')
        .setDescription('Kanalı açar (mesaj gönderimini tekrar açar).')
        .setDefaultMemberPermissions(PermissionFlagsBits.ManageChannels),
    async execute(interaction) {
        try {
            await interaction.channel.permissionOverwrites.edit(interaction.guild.id, {
                SendMessages: null
            });
            
            await interaction.reply('🔓 Kanal kilidi kaldırıldı. Mesaj gönderilebilir.');
        } catch (error) {
            console.error('Unlock error:', error);
            await interaction.reply({ content: '❌ Kanal kilidi kaldırılamadı.', ephemeral: true });
        }
    }
};
